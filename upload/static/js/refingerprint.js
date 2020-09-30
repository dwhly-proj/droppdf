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

        $('#pdf-file').val(null);
        $('#filename').text('');

        $('#copy-count').val(1);

        //in_process = false;
    };

    function _showProcessed(file_htmls) {
        var el = $('#result-copies');

        $(el).empty();

        $.each(file_htmls, function(i, v) {
            $(el).append(v);
        });
    };

    function _uploadPDF() {
        //if (in_process) {
            //return;
        //};

        //console.log('asaa');
        //return
        //$('#param-form').submit();

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

        //$('#upload-button').addClass('disabled');
        //$('#wait-icon').show();
        //$('#pdf-file').prop('disabled', true);

        //var formData = new FormData();
        //formData.append('pdf_file', file); 

        //formData.append('copy_count', $('#copy-count').val());
        //formData.append('suffix', $('#file-suffix').val());

        //$.ajax({
            //url : '/refingerprint_upload/',
            //type: 'POST',
            //data: formData,
            //cache: false,
            //contentType: false,
            //processData: false,
            //dataType: 'json',
            ////dataType: 'multipart/form-data',
            //success: function(response) {
                //console.log(response);

                //if (response.files) {
                    //_restoreReady();
                    //_showProcessed(response.files);
                //} else {
                    //_showError('error processing the request')
                //}
            //},
            //error: function(e) {
                //console.log('error', e)
                //_restoreReady();
            //}
        //});
    };

    window.uploadPDF = _uploadPDF;
    window.updateFileName = _updateFileName;

}());
