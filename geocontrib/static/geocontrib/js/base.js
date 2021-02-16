$(document).ready(function() {
	// INITIALISATION SEMANTIC UI COMPONENTS
	// $('.ui.accordion').accordion()
	$('.ui.dropdown').dropdown('refresh')
	$('.menu .item').tab()

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
})
