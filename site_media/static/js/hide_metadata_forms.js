function hide_metadata_forms(form_class) {
    if (form_class == "add-section") {
        $('#add-property').hide();
        $('#add-dataset').hide();
        $('#add-datafile').hide();
        $('#add-timeseries').hide();
        $('#edit-property').hide();
        $('#add-odml').hide();
    };
    if (form_class == "edit-property") {
        $('#add-property').hide();
        $('#add-dataset').hide();
        $('#add-datafile').hide();
        $('#add-timeseries').hide();
        $('#form-add-section').hide();
        $('#add-odml').hide();
    };
    if (form_class == "add-dataset") {
        $('#add-property').hide();
        $('#edit-property').hide();
        $('#add-datafile').hide();
        $('#add-timeseries').hide();
        $('#form-add-section').hide();
        $('#add-odml').hide();
    };
    if (form_class == "add-property") {
        $('#edit-property').hide();
        $('#add-dataset').hide();
        $('#add-datafile').hide();
        $('#add-timeseries').hide();
        $('#form-add-section').hide();
        $('#add-odml').hide();
    };
    if (form_class == "add-datafile") {
        $('#add-property').hide();
        $('#add-dataset').hide();
        $('#edit-property').hide();
        $('#add-timeseries').hide();
        $('#form-add-section').hide();
        $('#add-odml').hide();
    };
    if (form_class == "add-timeseries") {
        $('#add-property').hide();
        $('#add-dataset').hide();
        $('#edit-property').hide();
        $('#add-datafile').hide();
        $('#form-add-section').hide();
        $('#add-odml').hide();
    };
    if (form_class == "import-odml") {
        $('#add-property').hide();
        $('#add-dataset').hide();
        $('#edit-property').hide();
        $('#add-datafile').hide();
        $('#form-add-section').hide();
        $('#add-timeseries').hide();
    };
};

