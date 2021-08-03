function parallax_height() {
  var scroll_top = $(this).scrollTop();
  var sample_section_top = $(".sample-section").offset().top;
  var header_height = $(".sample-header-section").outerHeight();
  $(".sample-section").css({ "margin-top": header_height+100 });
  $(".sample-header").css({ height: header_height+100 - scroll_top });
}
parallax_height();
$(window).scroll(function() {
  parallax_height();
});
$(window).resize(function() {
  parallax_height();
});



$(document).ready(function(){
  $('#act').on('change', function() {
    if (this.value == 'act2')
    {
      $("#act2").show();
      $("#act1").hide();
    }
    else if(this.value == 'act1')
    {
      $("#act2").hide();
      $("#act1").show();
    }
  });
});