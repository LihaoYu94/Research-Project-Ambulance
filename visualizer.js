//
// Configuration variables
//

var TYPE_BUSY = 0;
var TYPE_AVAILED = 1;
var TYPE_SNR = 2;
var TYPE_UNAVAILED = 3;

var img_amb_free = 'http://chart.apis.google.com/chart?chst=d_map_pin_icon&chld=medical|FF7777';
var img_amb_busy = 'http://chart.apis.google.com/chart?chst=d_map_pin_icon&chld=medical|000000';
var img_call_busy = 'http://chart.apis.google.com/chart?chst=d_map_pin_icon&chld=wheelchair|FF0000';
var img_call_availed = 'http://chart.apis.google.com/chart?chst=d_map_pin_icon&chld=wheelchair|00FF00';
var img_call_unavailed = 'http://chart.apis.google.com/chart?chst=d_map_pin_icon&chld=wheelchair|0000FF';
var img_call_snr = 'http://chart.apis.google.com/chart?chst=d_map_pin_icon&chld=wheelchair|FFFFFF';

//
// End configuration variables
//



// 
// Generates the info html for calls and bases
//
function genBasicCallInfo(call_id, total_time, segment_id) {
   return "Call_id: " + call_id  
      + "<br> total time: " + total_time 
      + "<br> Segment: " + segment_id;
}
function genBasicBaseInfo(amb_id, segment_id, arrival_rate) {
   return "Ambulance Number: " + amb_id
      + "<br> Segment: " + segment_id
      + "<br> Inter-Arrival Rate Time: " + arrival_rate;
}


//
// Utility functions
//

// performs binary search to find the call index for time t
function callIndexSearch (calls, t)
{
   var tot = calls.length;
   var upper = tot;
   var lower = 0;
   while(upper - lower > 1) {
      var curr = Math.floor((upper + lower)/2);
      if(calls[curr].startTime <= t) {
         lower = curr + 1;
      }
      else {
         upper = curr;
      }
   }
   return lower;
}


//
// defines a Call object
//
function Call (Lat,Lng,type,startTime,endTime,infoHTML,base) {
   this.startTime = startTime;
   this.endTime = endTime;

   this.info = new google.maps.InfoWindow({content: infoHTML});
   this.LatLng  = new google.maps.LatLng(Lat,Lng);

   this.active = 0;

   var img = null;
   switch(type)
   {
      case TYPE_BUSY:         img = img_call_busy; break;
      case TYPE_AVAILED:      img = img_call_availed; break;
      case TYPE_UNAVAILED:    img = img_call_unavailed; break;
      case TYPE_SNR:          img = img_call_snr; break;
   }
   this.marker =  new google.maps.Marker({
      position: this.LatLng,
      map: null,
      icon: img
   });

   // pointer to Base object
   // should be set to null for TYPE_BUSY and some TYPE_SNR
   this.base = base;

   // initializes the path object (if required)
   this.path = null;
   if(this.base != null) {
      var ords = [this.LatLng, this.base.LatLng];
      this.path = new google.maps.Polyline({
         path: ords,
         strokeColor: "#FF0000",
         strokeOpacity: 1.0,
         strokeWeight: 2.0,
         map: null,
      });
   }
}
// this function does the following 
// -- binds the call marker to the map canvas
// -- binds the infowindow 
// -- binds the base-to-call path to the map canvas (if required)
// -- recolors the base to busy (if required)
function activateCall(call,map) {
  if(call.active == 1) {
     return;
  }
  else {
     call.active = 1;
  }

  call.marker.setMap(map);
  if(call.path != null) {
     call.path.setMap(map);
  }
  if(call.base != null) {
    //TODO: Can this ever go negative?
    //YY: not if the code is bug-free
     call.base.freeAmbs--;
     if(call.base.freeAmbs == 0) {
        call.base.marker.setIcon(img_amb_busy);
     }
  }
  
  google.maps.event.addListener(call.marker, 'click', 
        function() {
           call.info.open(map, call.marker);
        }
     );
}


// this function does the following 
// -- unbinds the call marker
// -- unbinds the base-to-call path (if required)
// -- recolors the base to free (if required)
deactivateCall = function(call) {
  if(call.active == 0) {
     return;
  }
  else {
     call.active = 0;
  }

  call.marker.setMap(null);
  if(call.path != null) {
     call.path.setMap(null);
  }
  if(call.base != null) {
     call.base.marker.setIcon(img_amb_free);
     call.base.freeAmbs++;
  }
}


//
// defines a Base object
//
function Base(Lat,Lng,infoHTML,numAmbs,color) {
   this.LatLng  = new google.maps.LatLng(Lat,Lng);

   // all ambulances are free to start with
   this.numAmbs = numAmbs;
   this.freeAmbs = numAmbs;

   this.info = new google.maps.InfoWindow({content: infoHTML});

   // this is the object that will contain the color-coded circles
   if (color==null) {
		this.circle = null;
	}
	else {
		this.circle = new google.maps.Circle({
					map: null, 
					center: new google.maps.LatLng(Lat, Lng), 
					radius: 1500, 
					fillOpacity: 0.35, 
					strokeWeight: 2, 
					strokeOpacity: 0.8, 
					strokeColor: color, 
					fillColor: color
					});
	}

   this.marker = new google.maps.Marker({
      position:  this.LatLng,
      map: null,
      icon: img_amb_free
   });
}

function activateBase (base,map) {
  if (base.circle != null) { base.circle.setMap(map);
  }
  base.marker.setIcon(img_amb_free);
  base.marker.setMap(map);
  google.maps.event.addListener(base.marker, 'click', 
        function() {
           base.info.open(map, base.marker);
        }
     );
}


//
// defines the visualizer engine object
//
var Visualizer = {
  
   //
   // Member variables
   //
   
   //contains the array of calls and bases
   calls: null,
   bases: null,

   play: 0,  //set to 1 to enable playing
   timeInterval: 600*1000, //how much time passes each iteration in seconds
   startTime: 0,
   currentTime: 0, //current time
   endTime: 500,
   playInterval: 1000,  //time delay between iterations

   currCallIndex: 0,
   activeCalls: [],  //set of currently active calls
   activeCallsLog: [], //array of set of active calls at each iteration

   currTimeIndex: 0,  //index of the iterations
   maxTimeIndex: 0,

   map: null,

   externalRefreshFunc: null,

   //
   // Member functions
   //

   // call this function to start the simulation 
   start: function(canvas, calls, bases, startTime, endTime, externalRefreshFunc) {
      Visualizer.externalRefreshFunc = externalRefreshFunc;

      //initializes the data structures
      Visualizer.calls = calls;
      Visualizer.bases = bases;

      Visualizer.startTime = startTime;
	  Visualizer.currentTime = Visualizer.startTime;
      Visualizer.endTime = endTime;

      Visualizer.currCallIndex = 0;
      Visualizer.currTimeIndex = 0;
      Visualizer.maxTimeIndex = Math.ceil((Visualizer.endTime.getTime()-Visualizer.startTime.getTime())/Visualizer.timeInterval);

      Visualizer.computeActiveLog();

      // this code block initializes the map canvas
      var options = {
         zoom: 11, 
         center: new google.maps.LatLng(17.4, 78.5),
         mapTypeId: google.maps.MapTypeId.ROADMAP
      };
      Visualizer.map = new google.maps.Map(document.getElementById(canvas), options);

      Visualizer.play = 1;

      // initialize all the bases
      Visualizer.initAllBases();

      // this will draw any calls that arrive at time 0
      Visualizer.refresh();

      // this sets the timer to call incrementTime at regular intervals
      Visualizer.timer = window.setInterval(Visualizer.incrementTime, Visualizer.playInterval);
   },


   // this function should be called at the beginning of the simulation
   initAllBases: function() {
      for(var seg_id in Visualizer.bases) {
         activateBase(Visualizer.bases[seg_id],Visualizer.map);
      }
   },


   // this function gets called every time the timer is incremented
   incrementTime: function() {
      if(Visualizer.play == 1) {
         if(Visualizer.currentTime < Visualizer.endTime) {
            Visualizer.currentTime = new Date(Visualizer.currentTime.getTime() + Visualizer.timeInterval);
            Visualizer.currTimeIndex++;
            Visualizer.refresh();
			window.document.getElementById('txt').value=Visualizer.currentTime.toLocaleString();
         }
         else {
            // stops the visualization if at the end of time
            Visualizer.play = 0;
         }
      }
   },


   // this function checks currentTime and removes active calls that have ended
   removeStaleCalls: function() {
      for(var i=Visualizer.activeCalls.length-1; i>=0; i--) {
         if(Visualizer.activeCalls[i].endTime <= Visualizer.currentTime) {
            deactivateCall(Visualizer.activeCalls[i])
            Visualizer.activeCalls.splice(i,1);
         }
      }
   },


   // this function checks currentTime and curCallIndex and adds new active calls
   addNewCalls: function(draw) {
      var numCalls = Visualizer.calls.length;
      var ind = Visualizer.currCallIndex;
      var calls = Visualizer.calls;
      var curr = Visualizer.currentTime;
      var map = Visualizer.map;

      while(ind < numCalls && calls[ind].startTime <= curr) {
         Visualizer.activeCalls.push(calls[ind]);
         if(draw == 1) {
            activateCall(calls[ind],map);
         }
         ind++;
      }

      //updates the new call index
      Visualizer.currCallIndex = ind;
   },


   // this function refreshes the canvas image
   refresh: function()  {
      //remove calls that are no longer active
      Visualizer.removeStaleCalls();

      //add newly arrived calls
      Visualizer.addNewCalls(1);

      Visualizer.externalRefreshFunc();
   },


   // This function clears all calls and sets all ambulances to free
   clearAll: function() {
      for(var i=0;  i<Visualizer.calls.length; i++) {
         deactivateCall(Visualizer.calls[i]);
      }
      Visualizer.activeCalls = [];
   },


   // This function resets the visualtion to time t_index
   resetTime: function(t_index) {
      Visualizer.clearAll();

      Visualizer.currTimeIndex = t_index;
      Visualizer.currentTime = new Date(Visualizer.startTime.getTime() + (Visualizer.currTimeIndex*Visualizer.timeInterval));
      Visualizer.currCallIndex = callIndexSearch(Visualizer.calls, Visualizer.currentTime);

      for(var i=0; i<Visualizer.activeCallsLog[t_index].length; i++) {
         activateCall(Visualizer.activeCallsLog[t_index][i],Visualizer.map);
      }
      Visualizer.activeCalls = Visualizer.activeCallsLog[t_index].slice(0);

      Visualizer.play = 1;
   },


   //
   // This function computes the set of active calls at each time step
   // This is useful for when scrolling the time slider, we don't need
   // to recompute the set of active calls from scratch
   //
   computeActiveLog: function() {
      var currTime = Visualizer.currentTime;
      var currIndex = Visualizer.currCallIndex;
      var currActiveCalls = Visualizer.activeCalls.slice(0);

      Visualizer.activeCalls = [];
      Visualizer.activeCallsLog = [];

      //Visualizer.currentTime = 0;
      Visualizer.currCallIndex = 0;

      Visualizer.addNewCalls(0);
      Visualizer.activeCallsLog.push(Visualizer.activeCalls.slice(0));

      for(var t=1; t<=Visualizer.maxTimeIndex; t++) {
         Visualizer.currentTime = new Date(Visualizer.currentTime.getTime() + Visualizer.timeInterval);
         Visualizer.removeStaleCalls();
         Visualizer.addNewCalls(0);
         Visualizer.activeCallsLog.push(Visualizer.activeCalls.slice(0));
      }

      Visualizer.activeCalls = currActiveCalls.slice(0);
      Visualizer.currentTime = currTime;
      Visualizer.currCallIndex = currIndex;
   }

};
