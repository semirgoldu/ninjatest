
$(document).ready(function(){
    $(".heart").on("click", function() {
    $(this).toggleClass("is-active");
  });


	// Lift card and show stats on Mouseover
	$('#property-card').hover(function(){
			$(this).addClass('animate');
			$('div.carouselNext, div.carouselPrev').addClass('visible');
		 }, function(){
			$(this).removeClass('animate');
			$('div.carouselNext, div.carouselPrev').removeClass('visible');
	});


});
