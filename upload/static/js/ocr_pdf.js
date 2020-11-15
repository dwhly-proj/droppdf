(function() {

    /* 5 minute max time */
    var max = 60
    var c = 0


    var check_interval = setInterval(function() {
        $.post('/ocr_pdf_complete', {filename: OCR_FILE_NAME})
        .done(function(result) {
            clearInterval(check_interval);

            var download_link = '/static/drop-pdf/' + OCR_FILE_NAME
            var docdrop_link = '/pdf/' + OCR_FILE_NAME

            $('#in-progress').hide();
            $('#download-info').show();

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
        if (PROCESSING_ERROR != 'None') {
            clearInterval(check_interval);

            $('#in-progress').hide();
            $('#download-info').hide();
            $('#upload-error')
                .text(PROCESSING_ERROR)
                .show();
        }
    });


}());
