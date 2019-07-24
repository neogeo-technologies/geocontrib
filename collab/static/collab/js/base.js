$(document).ready(function() {

  // INITIALISATION SEMANTIC UI COMPONENTS
  $('.ui.accordion').accordion()
  // $('main .selection.dropdown').dropdown()
  // $('main .ui.checkbox').checkbox()
  // $('.message .close').on('click', function() {
    // $(this).closest('.message').hide()
  // })
  updateCSSMinHeight()

  $(window).resize(function(){
    updateCSSMinHeight()
  })

  function updateCSSMinHeight() {
    var body = parseInt($("body").css("height"),10)
    var header = parseInt($("header").css("height"),10)
    var footer = parseInt($("footer").css("height"),10)
    var main = (body) - (header+footer)
    $("main").css("min-height",main);
  }

  // $('.ui.sidebar').sidebar({
  //     context: $('.ui.pushable.segment'),
  //     transition: 'overlay'
  // }).sidebar('attach events', '#mobile_item');

})
