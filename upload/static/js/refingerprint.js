(function() {
    //var in_process = false;

    function _showError(m) {
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

        if (file.size > 104857600) {
            return 'file is too large (100MB limit)'
        };

        return null
    };

    function _updateFileName() {
        _hideError();

        var filename = '';

        var file = $('#pdf-file').prop('files')[0];

        if (file) {
            var check_error = _checkFileError(file);

            if (check_error) {
                _showError(check_error);

                return false;
            }

            filename = file.name;

            $('#filename').text(filename);
            $('#filesize').text(file.size + 'bytes');
        };

        return true;
    };

    function _restoreReady() {
        $('#upload-button').removeClass('disabled');
        $('#wait-icon').hide();
        $('#pdf-file').prop('disabled', false);

        $('#pdf-file').val(null);
        $('#filename').text('');

        $('#copy-count').val(1);

    };

    function _showProcessed(file_htmls) {
        var el = $('#result-copies');

        $(el).empty();

        $.each(file_htmls, function(i, v) {
            $(el).append(v);
        });
    };

    function _uploadPDF() {
        _hideError();

        var file = $('#pdf-file').prop('files')[0];

        if (! file) {
            return _showError('Please select a file first');
        }

        var check_error = _checkFileError(file);
        if (check_error) {
            return _showError(check_error);
        }

        $('#param-form').submit();

    };

    window.uploadPDF = _uploadPDF;
    window.updateFileName = _updateFileName;

}());
