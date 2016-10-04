
$(document).ready(function() {
    var table = $('#group_posts_table').DataTable( {
        "paging": false,
         order: [ 0, 'desc' ],
        "ajax": {
            "url": "data.json",
            "dataSrc": ""
        },
        "columns": [
            { "data": "dateposted" },
            { "data": "htmldesc" },
            { "data": "location" },
            { "data": "groupurltext" },
            { "data": "postid" },
        ]
    } );


    setInterval( function () {
        table.ajax.reload( null, false ); // user paging is not reset on reload
    }, 30000 );

    table.ajax.reload( function ( json ) {
        $('#group_posts_table').val( json.lastInput );
    } );

} );
