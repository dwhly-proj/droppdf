(function() {
    in_process = false;

    function _uploadPDF() {
        if (in_process) {
            return;
        }

        $('#upload-button').addClass('disabled');
        $('#wait-icon').show();
        in_process = true;
        
        var file = $('#pdf-file').prop('files')[0];


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
            success : function(response) {
                console.log(response);
            }
        });
    };

    window.uploadPDF = _uploadPDF;

}());
