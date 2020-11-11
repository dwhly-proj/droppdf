(function() {


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

        })
        .fail(function(e) {
            console.log(e)
        })
    }, 5000);


}());
