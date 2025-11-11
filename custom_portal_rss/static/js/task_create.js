$(document).ready(function () {
    $('#create_task_btn').on('click', function (event) {

        $('.error-message-new').hide();
        const form = $('#TaskDetailsForm')[0];
        const formData = new FormData(form);

        const project_id = formData.get('project_id')
        const poNumber = formData.get('po_number');
        const short_desc = formData.get('short_desc');
        const buyer_name = formData.get('buyer_id');
        const country_id = formData.get('country_id');
        console.log(country_id,buyer_id,short_desc)

        if (!buyer_name) {
            $('select[name="buyer_id"]').next('.error-message-new')
                .text("Buyer Name is required.")
                .show();

            return false;
        }

        if (!country_id) {
            $('select[name="country_id"]').next('.error-message-new')
                .text("Country is required.")
                .show();

            return false;
        }

        if (!short_desc || short_desc.trim() === '') {
            $('input[name="short_desc"]').next('.error-message-new')
                .text("Short Description is required.")
                .show();

            return false;
        }

         if (!poNumber || poNumber.trim() === '') {
            $('input[name="po_number"]').next('.error-message-new')
                .text("PO number is required.")
                .show();

            return false;
        }

        $.ajax({
            url: `/rss/task/create/${project_id}`,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response){
                alert("Task submitted successfully.");
                $('#create-article-modal').hide();
                $('.modal-overlay').hide();
                location.reload(true);
            },
            error: function(err){
                alert("Failed to submit task.");
            }
        });
    });
});

