$(document).ready(function () {
    requestData();
    setInterval(requestData, 1000);
});

function requestData() {
    $.ajax({
        url: updateUrl,
        dataType: 'json',
    }).done(function (data) {
        console.log(data);
        console.log(data["my_tests"]);
        updateData(data)
    });
}

function updateData(data) {
    $("#current_tests").html(data["current_tests"]);
}