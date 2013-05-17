var slug = function(str) {
    var $slug = '';
    var trimmed = $.trim(str);
    $slug = trimmed.replace(/[^a-z0-9-]/gi, '-').
    replace(/-+/g, '-').
    replace(/^-|-$/g, '');
    return $slug.toLowerCase();
}

$.ajax({
    url:      'api/gauges',
    method:   'GET',
    dataType: 'json',
    timeout:  1000,
    success:  function(data) {
        var gauges = data.gauges;
        for (var key in gauges) {
            var name = gauges[key]['port'];
            $('#gauge_container').empty()
            $('<div>', { id: slug(name), class: 'gauge' })
                    .append( $('<span>', { class: 'label', text: name }))
                    .append( $('<span>', { class: 'nickname editable', text: gauges[key]['nickname'] }))
                    .append( $('<div>', { class: 'value' }))
                    .appendTo('#gauge_container');
        }

        // setup common ajax setting
        $.ajaxSetup({
            type: 'POST',
            async: false,
            timeout: 500
        });
        $('.editable').inlineEdit({
            buttons: '<a href="#" class="save">✔</a> <a href="#" class="cancel">✘</a>',
            buttonsTag: 'a',
            cancelOnBlur: true,
            save: function(event, data) {
                var status = $.ajax({
                    url: 'api/nickname/'+ $(this).siblings('.label').text(),
                    data: { 'nickname': data.value }
                }).status;
                return status === 200 ? true : false;
            }

        });
    },
    error: function(xhr, textStatus, errorThrown){
        $('#gauge_container').empty()
        $('<div>', { class: 'note error', text: 'Sorry, could not connect to API server.' }).appendTo('#gauge_container');
    }
});

var tv = 500;
var iv = setInterval( function() {
    $.ajax({
        url:      'api/pressure/all',
        method:   'GET',
        dataType: 'json',
        timeout:  1000,
        success:  function(pressure) {
            for (var key in pressure) {
                $('#'+slug(key)).children('.value').html(pressure[key]['pressure'].toExponential(3).replace(/e/g, 'E'));
            }
        },
        error: function(xhr, textStatus, errorThrown){
        }
    });
}, tv );