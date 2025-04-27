require([
    'jquery',
    'splunkjs/mvc',
    'splunkjs/mvc/simplexml/ready!'
], function($, mvc) {
    $('#submit-config').on('click', function() {

        var url = document.getElementById('url');
        var url = url.value;
//        console.log('URL: ', data);

        var username = document.getElementById('username');
        var username = username.value;
//        console.log('Username: ', username);

        var password = document.getElementById('password');
        var password = password.value;
//        console.log('Password: ', password);

//	var jsonout = JSON.stringify({
//                url: url,
//                username: username,
//                password: password
//            });
//        console.log('json: ', jsonout);

        $.ajax({
            type: "POST",
            url: "/en-US/splunkd/__raw/servicesNS/-/adv_dashboards/update_creds",
            data: {
                url: url,
                username: username,
                password: password
            },
            success: function() {
                $('#response-msg').html('<p style="color:green;">Configuration saved!</p>');
            },
            error: function(xhr) {
                $('#response-msg').html('<p style="color:red;">Error: ' + xhr.responseText + '</p>');
            }

        });

    });
});
