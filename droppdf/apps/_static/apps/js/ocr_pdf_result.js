(function() {

    /* 50 minute max time */
    var max = 600
    var c = 0

    var stop_time;
    var start_time = new Date();

    function _show_complete() {
        clearInterval(check_interval);

        stop_time = new Date();

        var time_to_process = ((stop_time - start_time) / 1000).toFixed(2)

        $('#in-progress').hide();
        $('#download-info').show();

        $('#processing-time').text(time_to_process);

        $('#docdrop-link').attr('href', '/pdf/' + FILE_INFO.processed_filename + '?src=ocr')

        $('#file-download-link').attr('href', FILE_INFO.download_url)
    };


    var check_interval = setInterval(function() {
        $.post('/ocr/check_complete', {filename: FILE_INFO.new_filename,
               task_id: FILE_INFO.task_id, csrfmiddlewaretoken: CSRF_TOKEN})
        .done(function(result) {
            //console.log(result);
            var error_detail_text;

            if (result.status == 'SUCCESS') {
                _show_complete();
                return;
            }
            else if (result.error_detail) {
                var error_detail = JSON.parse(result.error_detail);

                if (error_detail.exc_type === 'MaxProcessesExceededError') {
                    error_detail_text = 'This service is currently limited to 3 concurrent OCR tasks.  Please try again in a few minutes.'

                }
            };

            if (! error_detail_text) {
                error_detail_text= result.status;
            };

            clearInterval(check_interval);

            $('#in-progress').hide();
            $('#download-info').hide();
            $('#upload-error')
                .text('Error Processing File.' + error_detail_text)
                .show();

            return
        })
        .fail(function(e) {
        });

        c += 1

        if (c > max) {
            clearInterval(check_interval);
            $('#in-progress').hide();
            $('#download-info').hide();
            $('#upload-error').show();

        };
    }, 5000);

    $(document).ready(function() {
        var url;

        $('#time-start').text(start_time.toLocaleTimeString());

        if (FILE_INFO && FILE_INFO.download_url && FILE_INFO.download_url.length > 0) {
            url = FILE_INFO.download_url;
        }

        $('#download-link')
            .attr('href', url)
            .text(url);

        $('#docdrop-link')
            .attr('href', '/pdf/' + FILE_INFO.new_filename + '?src=ocr')
            .text(FILE_INFO.new_filename);

        /* ocr previously performed */
        if (FILE_INFO.download_url && FILE_INFO.existing) {
            clearInterval(check_interval);
            _show_complete();
        }

        else if (FILE_INFO.processing_error) {
            clearInterval(check_interval);

            $('#in-progress').hide();
            $('#download-info').hide();
            $('#upload-error')
                .text(FILE_INFO.processing_error)
                .show();
        }
    });

}());
