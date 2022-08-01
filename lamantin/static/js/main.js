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
  $('#textModal').submit(function(e){
    e.preventDefault();
    var $body = $('#id_body').val();
    var $oid = $('#id_oid').val();
    var $mod = $('#id_mod').val();
    var $fld = $('#id_fld').val();
    $.ajax({
      type: 'POST',
      url: $manager,
      data: {'aid':$aid,'value':$body,'mod':$mod,'oid':$oid,'name':$fld},
      cache: false,
      beforeSend: function(){
        $('#textModal').modal('hide');
      },
      success: function(data){
        if (data['id']) {
          $id = ''
          if ($fld) {
            $id = $fld + '_'
          }
          $('#oid_' + $id + data['id']).replaceWith(data['msg']);
        } else {
          $('#comments-list').prepend(data['msg']);
        }
        $('#id_body').val('');
        $('.modal-backdrop').remove();
      },
      error: function(data){
        //console.log(data);
        $.growlUI($mod + " Form", "Error");
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
});
