        $(document).ready(function() {
            $('#edit-details-toggle').click(function() {
                $('#change-privacy').hide();
                $('#edit-details').toggle();
                $('#edit-details').autoscroll();
                return false;
            });
            if ($('#edit-details .error').length) {
                $('#change-privacy').hide();
                $('#edit-details').show();
                $('#edit-details .error').autoscroll();
            };
            $('#change-privacy-toggle').click(function() {
                $('#edit-details').hide();
                $('#change-privacy').toggle();
                $('#change-privacy').autoscroll();
                return false;
            });
            if ($('#change-privacy .error').length) {
                $('#edit-details').hide();
                $('#change-privacy').show();
                $('#change-privacy .error').autoscroll();
            }
        });
