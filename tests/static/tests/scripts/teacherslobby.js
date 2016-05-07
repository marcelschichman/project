$(document).ready(function () {
    $.ajax({
        url: updateUrl,
        dataType: 'json',
    }).done(function (data) {
        console.log(data);
        console.log(data["my_tests"]);
        updateData(data)
    });
});

function updateData(data) {
    $("#my_tests").html(data["my_tests"]);
    if ("results" in data) {
        $("#test_results").html(data["results"]);
    }
}

function activateTest(testId) {
    $.ajax({
        url: updateUrl,
        method: "POST",
        data: { "activate": testId },
        dataType: 'json',
    }).done(function (data) {
        updateData(data);
    });
}

function deactivateTest(testId) {
    $.ajax({
        url: updateUrl,
        method: "POST",
        data: { "deactivate": testId },
        dataType: 'json',
    }).done(function (data) {
        updateData(data);
    });
}

function showResults(testId) {
    $.ajax({
        url: updateUrl,
        method: "POST",
        data: { "results": testId },
        dataType: 'json',
    }).done(function (data) {
        updateData(data);
    });
}