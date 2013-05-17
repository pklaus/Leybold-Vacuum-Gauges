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
            var name = gauges[key];
            $('#gauge_container').empty()
            $('<div>', { id: slug(name), class: 'gauge' })
                    .append( $('<div>', { class: 'label', text: name }))
                    .append( $('<div>', { class: 'value' }))
                    .appendTo('#gauge_container');
        }
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