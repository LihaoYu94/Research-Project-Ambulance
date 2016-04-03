
function initControls()
{
   // starts up the slider
   $( "#slider" ).slider({
      value:0,
      min: 0,
      max: Visualizer.maxTimeIndex,
      step: 1,
      slide: function( event, ui ) {
         Visualizer.resetTime(ui.value);
      }
   });

   $("#start_stop").click(function() {
      Visualizer.play = 1 - Visualizer.play;
   });
}

// this function should be passed as an argument into Visualizer.start(...)
// it will be called every time Visualizer refreshes
function refreshControls()
{
   // updates the slider header position
   $( "#slider" ).slider("option", "value", Visualizer.currTimeIndex);
}
