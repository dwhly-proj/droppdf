(function() {

    /* 50 minute max time */
    var max = 600
    var c = 0

    var stop_time;
    var start_time = new Date();


    var check_interval = setInterval(function() {
        $.post('/ocr_pdf_complete', {filename: OCR_FILE_NAME})
        .done(function(result) {
            clearInterval(check_interval);

            stop_time = new Date();

            var download_link = '/static/drop-pdf/' + OCR_FILE_NAME
            var docdrop_link = '/pdf/' + OCR_FILE_NAME

            var time_to_process = ((stop_time - start_time) / 1000).toFixed(2)

            $('#in-progress').hide();
            $('#download-info').show();

            $('#processing-time').text(time_to_process);

            $('#file-docdrop-link').attr('href', '/pdf/' + OCR_FILE_NAME)
            $('#file-download-link').attr('href', '/static/drop-pdf/' + OCR_FILE_NAME)

            return;

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
        $('#time-start').text(start_time.toLocaleTimeString());

        var url = window.location.origin;
        url += '/static/drop-pdf/' + OCR_FILE_NAME;

        $('#download-link').text(url);

        if (PROCESSING_ERROR != 'None' || !PROCESSING_ERROR || PROCESSING_ERROR === '') {

            clearInterval(check_interval);

            $('#in-progress').hide();
            $('#download-info').hide();
            $('#upload-error')
                .text(PROCESSING_ERROR)
                .show();
        }
    });

}());
