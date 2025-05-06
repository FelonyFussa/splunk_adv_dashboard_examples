require([
    'jquery',
    'splunkjs/mvc',
    'splunkjs/mvc/simplexml/ready!'
], function($, mvc) {
    let serverCounter = 0;

    // Add a new Server Type 2 section
    $('#add-server').on('click', function () {
        serverCounter++;
        const clone = $('#server-template .server-block').clone();

        // Optional: label each block uniquely
        clone.find('h3').text(`Server Type 2 - ${serverCounter}`);
        $('#dynamic-server-blocks').append(clone);
    });

    // Submit config
    $('#submit-config').on('click', function () {
        let data = [];

        // Server Type 1
        data.push({
            type: "server1",
            url: $('#url').val(),
            username: $('#username').val(),
            password: $('#password').val()
        });

        // Server Type 2 (all dynamic blocks)
        $('#dynamic-server-blocks .server-block').each(function (index, element) {
            data.push({
                type: `server2-${index + 1}`,
                url: $(element).find('.url').val(),
                username: $(element).find('.username').val(),
                password: $(element).find('.password').val()
            });
        });

        var post = JSON.stringify({ servers: data });
        console.log(post);

        $.ajax({
            type: "POST",
            url: "/en-US/splunkd/__raw/servicesNS/-/adv_dashboards/dyn_creds",
            data: {
                servers: data
            },
            success: function () {
                $('#response-msg').html('<p style="color:green;">Configuration saved!</p>');
            },
            error: function (xhr) {
                $('#response-msg').html('<p style="color:red;">Error: ' + xhr.responseText + '</p>');
            }
        });
    });
});
