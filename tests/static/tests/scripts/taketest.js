
var tasks = {}

$(document).ready(function () {
    if (test_data != '') {
        for (task in test_data) {
            addTask(test_data[task]);
        }
    }
    $("#submit_test").click(function() {
        tasks2send = []
        if (UpdateAndValidate()) {
            for (var task in tasks) {
                delete tasks[task]["dom_id"];
                tasks2send.push(tasks[task]);
            }
            console.log(JSON.stringify(tasks2send));
            $("#test_data_hidden").val(JSON.stringify(tasks2send));
            $("#test_name_hidden").val($("#test_name").val());
        }
        else {
            return false;
        }
    });
});

function addTask(task) {
    var taskElement;
    switch (task.type) {
        case "text":
            taskElement = renderTextTask(task); break;
        case "choice":
            taskElement = renderChoiceTask(task); break;
        default:
            return;
    }
    $("#tasks").append(taskElement);
    tasks[taskElement.attr('id')] = task;
    task['dom_id'] = taskElement.attr('id');
    $("<div>", {"class": "errors"}).appendTo(taskElement);
}

function renderTextTask(task) {
    var taskDiv = $("<div>", {
        "class": "task panel panel-default",
        "id": generateDomID()
    });
    $("<div>", {
        "class": "assignment panel-heading",
    }).html(task.assignment).appendTo(taskDiv);
    var panelBody = $("<div>", {"class": "panel-body"}).appendTo(taskDiv);
    $("<textarea>", {
        "class": "answer form-control"
    }).appendTo(panelBody);
    return taskDiv;
}

function renderChoiceTask(task) {
    var taskDiv = $("<div>", {
        "class": "task panel panel-default",
        "id": generateDomID()
    });
    $("<div>", {
        "class": "assignment panel-heading",
    }).html(task.assignment).appendTo(taskDiv);
    var choicesDiv = $("<div>", {"class": "choices panel-body"}).appendTo(taskDiv);
    for (var choice in task["choices"]) {
        renderChoice("choice_" + taskDiv.attr("id"), task["choices"][choice], false).appendTo(choicesDiv);
    }
    return taskDiv;
}

function renderChoice(name, content = "", checked = false) {
    var choiceDiv = $("<div>", {"class" : "choice"});
    $("<input>", {"type": "radio", "name": name, "value": content}).prop("checked", checked).appendTo(choiceDiv);
    $("<span>", {"class": "choice_text"}).html(content).appendTo(choiceDiv);
    return choiceDiv;
}

var idCounter = 0;
function generateDomID() {
    return "task_" + (idCounter++);
}

function UpdateAndValidate() {
    ResetErrors();
    var success = true;
    for (var taskId in tasks) {
        task = tasks[taskId];
        var taskDiv = $("#" + task["dom_id"]);
        if (task["type"] == "text") {
            task["answer"] = $("textarea", taskDiv).val();
        } else if (task["type"] == "choice") {
            if ($("input[type=radio]:checked", taskDiv).size() == 0) {
                AddError(task, "Nevybrali ste ani jednu odpoveď.");
                success = false;
            }
            task["answer"] = $("input[type=radio]:checked", taskDiv).val();
        }
    }
    return success;
}

function AddError(task, error) {
    var errorDiv = $("#" + task["dom_id"] + " .errors");
    if (errorDiv.html() != "") {
        errorDiv.append("<br />");
    }
    $("<div>", {"class": "bg-danger"}).html(error).appendTo(errorDiv);
}

function ResetErrors() {
    for (var task in tasks) {
        $("#" + task + " .errors").empty();
    }
}