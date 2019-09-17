$(function() {
    $('#generate').click(function() {
        $.ajax({
            url: '/sucess',
            data: $('#BidsForm').serialize(),
            type: 'POST',
            success: function(response) {
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
    });

 $(function() {
    $('#login').click(function() {
        $.ajax({
            url: '/',
            data: $('#loginForm').serialize(),
            type: 'POST',
            success: function(response) {
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
  });

$(function() {
    $('#go').click(function() {
        $.ajax({
            url: '/fetchData/',
            data: $('#auctionForm').serialize(),
            type: 'POST',
            success: function(response) {
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
    });

    $(function() {
        $('#newAuction').click(function() {
            $.ajax({
                url: '/auctionForm/',
                data: $('#newAuctionForm').serialize(),
                type: 'POST',
                success: function(response) {
                    console.log(response);
                },
                error: function(error) {
                    console.log(error);
                }
            });
        });
        });

$(function() {
    $('#download').click(function() {
        $.ajax({
            url: '/download/',
            data: $('#downloadForm').serialize(),
            type: 'POST',
            success: function(response) {
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
    });

    
