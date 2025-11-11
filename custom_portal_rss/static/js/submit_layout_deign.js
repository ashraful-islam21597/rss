$(document).ready(function () {
    $('#submit_layout_design_btn').on('click', function (event) {
        event.preventDefault();

        $('.error-message-new').hide();
        const form = $('#submit_layout_form')[0];
        const formData = new FormData(form);

        const task_id = formData.get('task_id')
        const layoutFiles = form.querySelector('input[name="layout_file[]"]').files;


        if (!layoutFiles || layoutFiles.length === 0) {
            $('input[name="layout_file[]"]').nextAll('.error-message-new').first()
                .text("Please attach at least one layout file.")
                .show();
            return false;
        }

        $.ajax({
            url: '/rss/design/task/save',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response){
                alert("Layout design uploaded");
                location.reload(true);
            },
            error: function(err){
                alert("Failed to submit task.");
            }
        });
    });
});


