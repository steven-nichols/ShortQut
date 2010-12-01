#!/usr/bin/env python
import os
import random

import testtalker

import gobject
import champlaingtk
import champlain
import champlainmemphis
import gtk
import clutter

def gpsfiletoroute(filename):
    f = open(filename, 'r')
    return map(lambda line: (float(line[1]), float(line[2])),
               map(lambda l: l.split(),
                   f.readlines()))

class ShortqutGUI:
    
    def __init__(self):
        global location
        global talker
        global loading
        global track
        global marker
        global auto_center
        talker = testtalker.TestTalker("data/gps2.out", 0)
        talker.runLoop()
        auto_center = True
        loading = True
        track = [] #where I've been

        self.window = gtk.Window()
        self.window.set_border_width(10)
        self.window.set_title("Shortqut v0.5a")
        self.window.connect("destroy", lambda x: self.cleanup())

        vbox = gtk.VBox(False, 12) 

        champ = champlaingtk.ChamplainEmbed()
        champ.set_size_request(640,480)

        self.view = champ.get_view()
        self.view.set_reactive(True)
        self.view.connect('button-release-event', self.mouse_click_cb, self.view)

        self.view.set_property('scroll-mode', champlain.SCROLL_MODE_KINETIC)
        self.view.set_property('zoom-level', 15)
        self.view.set_property('license-text', ".")
        self.view.set_property('show-scale', True)
        
        layer = champlain.Layer()
        self.view.add_layer(layer)
        
        self.map_source_factory = champlain.map_source_factory_dup_default()
        self.map_data_source = None
        self.load_memphis_rules()
        self.load_osm_file()
        
        #Add the image
        '''
        bboxTitle = gtk.HBox(False, 6)
        image = gtk.Image()
        image.set_from_file("Shortqut_banner.jpg")
        bboxTitle.add(image)
        image.show()
        vbox.pack_start(bboxTitle, expand = False, fill = False)
        '''
        
        #Add the buttons
        bbox = gtk.HBox(False, 6)

        #Add the label
        self.label = gtk.Label("Loading OSM File")
        bbox.add(self.label)

        center_check = gtk.CheckButton("Centered")
        center_check.set_active(True)
        center_check.connect("clicked", self.toggle_auto_centered)
        bbox.add(center_check)
        
        button = gtk.Button(stock=gtk.STOCK_ZOOM_IN)
        button.connect("clicked", self.zoom_in)
        bbox.add(button)

        button = gtk.Button(stock=gtk.STOCK_ZOOM_OUT)
        button.connect("clicked", self.zoom_out)
        bbox.add(button)

        
        
        self.spinbutton = gtk.SpinButton(gtk.Adjustment(lower=0, upper=20, 
            value=1, step_incr=1))
        self.spinbutton.connect("changed", self.zoom_changed)
        self.view.connect("notify::zoom-level", self.map_zoom_changed)
        self.spinbutton.set_value(15)
        bbox.add(self.spinbutton)

        button = gtk.Image()
        self.view.connect("notify::state", self.view_state_changed, button)
        bbox.pack_end(button, False, False, 0)        

        vbox.pack_start(bbox, expand=False, fill=False)
        vbox.add(champ)

        self.window.add(vbox)

        self.window.show_all()


        #lat = 28.568542 + (random.random() - 0.5)
        #lon = -81.207504 + (random.random() - 0.5)
        lat = 28.541492
        lon = -81.195965
        self.view.center_on(lat,lon)
        
        
        #Set up and position sprite
        actor = clutter.Texture(filename="pirate-ship-1.jpg")
        marker = champlain.marker_new_with_image(actor)
        marker.set_draw_background(False)
        #marker.set_position(0,0)
        marker.set_position(lat,lon)
        layer.add(marker)
        marker.raise_top()

        self.draw_route(gpsfiletoroute("data/gps2.out"))

        location = talker.getMsg()
        #gobject.timeout_add(1000, random_view, self.view)
        gobject.timeout_add(500, center_gps, self.view, location)
        gobject.timeout_add(1000, is_loaded, self.view, self.label)

    def cleanup(self):
        global talker
        talker.setRunning(False)
        gtk.main_quit()
        
    def draw_route(self, list_of_points, color='blue'):
        route = champlain.Polygon()
        for x in list_of_points:
            route.append_point(x[0], x[1])
        route.set_stroke_width(5.0)
        route.set_stroke_color(clutter.color_from_string(color))
        self.view.add_polygon(route)
        
    #If the box is checked, enable Automatic Centering
    def toggle_auto_centered(self, widget):
        global auto_center
        auto_center = False if auto_center else True
    
    def zoom_in(self, widget):
        self.view.zoom_in()

    def zoom_out(self, widget):
        self.view.zoom_out()

    def mouse_click_cb(self, actor, event, view):
        lat, lon = view.get_coords_from_event(event)
        print "Mouse click at: %f %f" % (lat, lon)
        self.view.center_on(lat, lon)
        return True

    def zoom_changed(self, widget):
        self.view.set_property("zoom-level", self.spinbutton.get_value_as_int())

    def map_zoom_changed(self, widget, value):
        self.spinbutton.set_value(self.view.get_property("zoom-level"))

    def view_state_changed(self, view, paramspec, image):
        state = view.get_property("state")
        if state == champlain.STATE_LOADING:
            image.set_from_stock(gtk.STOCK_HARDDISK, gtk.ICON_SIZE_BUTTON)
        else:
            image.set_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON)

    def load_osm_file(self):
        osm_filename = "orlandoeast.osm"
        if not os.path.isfile(".%s%s" % (os.sep, osm_filename)):
            print "no valid OSM file"
            return
        
        self.map_data_source = champlainmemphis.LocalMapDataSource()
        
        #gobject.idle_add(self._load_osm_file, osm_filename)
        gobject.timeout_add(10, self._load_osm_file, osm_filename)
		
    def _load_osm_file(self, filename):
        global loading
        print "Loading osm file..."
        self.map_data_source.load_map_data(".%s%s" % (os.sep, filename))
        print "Done"

        loading = False
        
        self.source.set_map_data_source(self.map_data_source)
        return False

    def load_memphis_rules(self):
        self.source = self.map_source_factory.create("memphis-local")
        if self.map_data_source is not None:
            self.source.set_map_data_source(self.map_data_source)
            
        rules_filename = "rules.xml"
        self.source.load_rules(".%s%s" % (os.sep, rules_filename))
                
        tile_size = self.source.get_tile_size()
        error_tile_source = champlain.error_tile_source_new_full(tile_size)
        
        file_cache_path = ".%scache" % (os.sep)
        file_cache = champlain.file_cache_new_full(1024*1024*50, file_cache_path, True)
        
        source_chain = champlain.MapSourceChain()
        source_chain.push(error_tile_source)
        source_chain.push(self.source)
        source_chain.push(file_cache)
        self.view.set_map_source(source_chain)

def random_view(view):
    if(not (view.get_property("state") == champlain.STATE_LOADING)):
        lat = 28.568542 + (random.random() - 0.5)
        lon = -81.207504 + (random.random() - 0.5)
        print "Go to: %f %f" % (lat, lon)
        view.center_on(lat, lon)
    return True

def center_gps(view, gps_tuple):
    global auto_center
    global marker
    global location
    global talker
    global track
    if talker.messages.qsize() > 0:
        location = talker.getMsg()
        time, lat, lon = location
        marker.set_position(lat,lon)
    if len(track) > 0:
        pass
        
    print "Go to: %f %f %f" % (time, lat, lon)
    if auto_center:
        view.center_on(lat, lon)
    return True

       
def is_loaded(view, label):
    global loading
    if loading:
        return True # have the timer run this fn again
    else:
        label.set_text("ShortQut")
        view.zoom_in()
        return False # the timer will fizzle out

if __name__ == "__main__":
    gobject.threads_init()
    ShortqutGUI()
    gtk.main()
