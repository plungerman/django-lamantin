/* spinner: instantiate */
var opts = {
  lines: 13, // The number of lines to draw
  length: 20, // The length of each line
  width: 10, // The line thickness
  radius: 30, // The radius of the inner circle
  corners: 1, // Corner roundness (0..1)
  rotate: 0, // The rotation offset
  direction: 1, // 1: clockwise, -1: counterclockwise
  color: '#000', // #rgb or #rrggbb or array of colors
  speed: 1, // Rounds per second
  trail: 60, // Afterglow percentage
  shadow: false, // Whether to render a shadow
  hwaccel: false, // Whether to use hardware acceleration
  className: 'search-results', // The CSS class to assign to spinner
  zIndex: 2e9, // The z-index (defaults to 2000000000)
  top: '50px', // Top position relative to parent in px
  left: 'auto' // Left position relative to parent in px
};
var target = document.getElementById('page-top');
var spinner = new Spinner(opts).spin(target);
spinner.stop(target);

$(function(){
  /* bootstrap popovers */
  $('[data-toggle="popover"]').popover();
  /* wysiwyg textarea editory */
  var $trumBowygDict = {
    btns: [
      ['formatting'], ['strong', 'em', 'del'], ['link'],
      ['unorderedList', 'orderedList'], ['horizontalRule'], ['viewHTML'],
    ],
    tagsToRemove: ['script', 'link'], urlProtocol: true,
    removeformatPasted: true, semantic: true, autogrow: true, resetCss: true
  };
  $('textarea').trumbowyg($trumBowygDict);
  /* datatables initialization for vaccine verification data */
  $('#courses').DataTable({
    'lengthMenu': [
      [100, 250, 500, 1000, 2000, 5000, 10000],
      [100, 250, 500, 1000, 2000, 5000, 10000]
    ],
    'language': {
      'search': 'Filter records:',
      'lengthMenu': 'Display _MENU_'
    },
    order: [[0, 'asc']],
    dom: 'lfrBtip',
    responsive: true,
    buttons: [
      {
        extend: 'excelHtml5',
        exportOptions: {
          columns: ':visible'
        }
      }
    ]
  });
  /* clear django cache object by cache key and refresh content */
  $('.clear-cache').on('click', function(e){
    e.preventDefault();
    var $dis = $(this);
    var $cid = $dis.attr('data-cid');
    var $target = '#' + $dis.attr('data-target');
    var $html = $dis.html();
    $dis.html('<i class="fa fa-refresh fa-spin"></i>');
    $.ajax({
      type: 'POST',
      url: $clearCacheUrl,
      data: {'cid':$cid},
      success: function(data) {
        $.growlUI("Cache", "Clear");
        $($target).html(data);
        $dis.html('<i class="fa fa-refresh"></i>');
      },
      error: function(data) {
        $.growlUI("Error", data);
      }
    });
    return false;
  });
  /* modal form for textarea data */
  $(document).on('click','.text-update', function (e) {
    var $dis = $(this);
    var $nid = $dis.attr('data-nid');
    console.log($nid);
    if ($nid) {
      $.ajax({
        url: $annotation,
        type: 'post',
        data: {'cid': $cid, 'action': 'fetch', 'nid': $nid},
        success: function(data){
          // Add response in Modal body
          $('#id_nid').val(data['id']);
          $('#id_body').val(data['msg']);
          $('#textModalHeader').text('Update comment');
          // Display Modal
          $('#id_body').trumbowyg('destroy');
          $('#textModal').modal('show');
          $('#id_body').trumbowyg($trumBowygDict);
        }
      });
    } else {
        if ($mod == 'comment') {
          $('#id_nid').val(0);
          $('#id_body').val('');
          $('#textModalHeader').text('New comment');
          // Display Modal
          $('#id_body').trumbowyg('destroy');
          $('#textModal').modal('show');
          $('#id_body').trumbowyg($trumBowygDict);
        }
    }
  });

  $('#textModal').submit(function(e){
    e.preventDefault();
    var $body = $('#id_body').val();
    var $nid = $('#id_nid').val();
    $.ajax({
      type: 'POST',
      url: $annotation,
      data: {'cid': $cid, 'nid': $nid, 'value': $body},
      cache: false,
      beforeSend: function(){
        $('#textModal').modal('hide');
      },
      success: function(data){
        if (data['id']) {
          $('#nid_' + data['id']).replaceWith(data['msg']);
        } else {
          $('#comments-list').prepend(data['msg']);
        }
        $('#id_body').val('');
        $('.modal-backdrop').remove();
        console.log('success');
        console.log(data);
      },
      error: function(data){
        console.log(data);
        $.growlUI("Form", "Error");
      }
    });
    return false;
  });
  $('#textModal').on('shown.bs.modal', function () {
    $('#id_body').focus();
  })
  $('#textModal').on('hidden.bs.modal', function () {
    $('#id_body').trumbowyg('destroy');
    $('#id_body').trumbowyg($trumBowygDict);
  });
  $('#confirm-delete').on('show.bs.modal', function(e) {
    $(this).find('.btn-ok').attr('href', $(e.relatedTarget).data('href'));
    $('.object-title').text( $(e.relatedTarget).data('title') );
  });
});
