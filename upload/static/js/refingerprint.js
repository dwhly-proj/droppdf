(function() {
    var in_process = false;

    function _showError(m) {
        console.log(m);

        $('#upload-error')
            .text(m)
            .show();
    };

    function _hideError() {
        $('#upload-error')
            .text('')
            .hide();
    };

    function _checkFileError(file) {
        //check file type and size
        //return null if good, otherwise return error.

        _hideError();

        if (file.type.indexOf('pdf') === -1) {
            return 'document is not a pdf!'
        };

        if (file.size > 12582912) {
            return 'file is too large (12MB limit)'
        };

        return null
    };

    function _updateFileName() {
        _hideError();

        var filename = '';

        var file = $('#pdf-file').prop('files')[0];

        if (file) {
            var check_error = _checkFileError(file);

            console.log('aaa', check_error);

            if (check_error) {
                return _showError(check_error);
            }

            filename = file.name;

            $('#filename').text(filename);
        };
    };

    function _restoreReady() {
        $('#upload-button').removeClass('disabled');
        $('#wait-icon').hide();
        $('#pdf-file').prop('disabled', false);
    };

    function _uploadPDF() {
        if (in_process) {
            return;
        };

        _hideError();

        var file = $('#pdf-file').prop('files')[0];

        if (! file) {
            return _showError('Please select a file first');
        }

        var check_error = _checkFileError(file);
        if (check_error) {
            return _showError(check_error);
        }

        in_process = true;

        $('#upload-button').addClass('disabled');
        $('#wait-icon').show();
        $('#pdf-file').prop('disabled', true);

        var formData = new FormData();
        formData.append('pdf_file', file); 

        formData.append('copy_count', $('#copy-count').val());

        $.ajax({
            url : '/refingerprint_upload/',
            type: 'POST',
            data: formData,
            cache: false,
            contentType: false,
            processData: false,
            dataType: 'multipart/form-data',
            success: function(response) {
                _restoreReady();
            },
            error: function(e) {
                console.log(e)
                _restoreReady();
            }
        });
    };

    window.uploadPDF = _uploadPDF;
    window.updateFileName = _updateFileName;

}());
