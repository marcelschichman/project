
var tasks = {}


function createTextTask() {
    var task = {
        "type": "text",
        "assignment": ""
    }
    return task;
}
function createChoiceTask() {
    var task = {
        "type": "choice",
        "assignment": "",
        "choices": [],
        "correct": null
    }
    return task;
}

$(document).ready(function () {
    if (test_data != '') {
        for (task in test_data) {
            addTask(JSON.parse(test_data[task]));
        }
    }
    $("#add_task_text").click(function() {
        addTask(createTextTask());
    });
    $("#add_task_choice").click(function () {
        addTask(createChoiceTask());
    });
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
        "class": "task well well-lg",
        "id": generateDomID()
    });
    var inputGroup = $("<div>", {"class": "input-group"}).appendTo(taskDiv);
    $("<input>", {
        "type": "text",
        "class": "form-control",
        "placeholder": "Znenie úlohy"
    }).val(task.assignment).appendTo(inputGroup);
    var inputGroupBtn = $("<div>", {"class": "input-group-btn"}).appendTo(inputGroup);
    renderRemoveButton().appendTo(inputGroupBtn);
    return taskDiv;
}

function renderChoiceTask(task) {
    var taskDiv = renderTextTask(task);
    var choicesDiv = $("<div>", {"class": "choices"}).appendTo(taskDiv);
    if (task["choices"].length == 0) {
        renderChoice("choice_" + taskDiv.attr("id")).appendTo(choicesDiv);
    } else {
        for (var choice in task["choices"]) {
            renderChoice("choice_" + taskDiv.attr("id"), task["choices"][choice], task["choices"][choice]==task["correct"]).appendTo(choicesDiv);
        }
    }
    $("<button>", {"class": "add_choice btn btn-default"}).click(function() {
        renderChoice("choice_" + taskDiv.attr("id"), choice).appendTo(choicesDiv);
    }).html("<span class=\"glyphicon glyphicon-plus\"></span>").appendTo(taskDiv);
    return taskDiv;
}

function renderChoice(name, content = "", checked = false) {
    var choiceDiv = $("<div>", {"class" : "choice input-group"});
    var inputGroupAddon = $("<div>", {"class": "input-group-addon"}).appendTo(choiceDiv);
    $("<input>", {"type": "radio", "name": name}).prop("checked", checked).appendTo(inputGroupAddon);
    $("<input>", {"type": "text", "class": "form-control"}).val(content).appendTo(choiceDiv);
    var inputGroupBtn = $("<div>", {"class": "input-group-btn"}).appendTo(choiceDiv);
    $("<button>", {"class": "delete_choice btn btn-default"}).html("<span class=\"glyphicon glyphicon-remove\"></span>&nbsp;").click(function() {
        $(this).parents(".choice").remove();   
    }).appendTo(inputGroupBtn);
    return choiceDiv;
}

function renderRemoveButton() {
    var removeButton = $("<button>", { "class": "delete_task btn btn-danger" }).append("<span class=\"glyphicon glyphicon-remove\"></span>&nbsp;").click(function (el) {
        var taskDiv = $(el.target).parents(".task");
        delete tasks[taskDiv.attr('id')];
        taskDiv.remove();
    });
    return removeButton;
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
            if ($("input", taskDiv).val() == "") {
                AddError(task, "Zadanie úlohy nesmie byť prázdne.");
                success = false;
            }
            task["assignment"] = $("input", taskDiv).val();
        } else if (task["type"] == "choice") {
            if ($("input", taskDiv).val() == "") {
                AddError(task, "Zadanie úlohy nesmie byť prázdne.");
                success = false;
            }
            var choices = [];
            var correct = null;
            $(".choices .choice", taskDiv).each(function() {
                if ($("input[type=text]", this).val() != "") {
                    choices.push($("input[type=text]", this).val());
                    if ($("input[type=radio]", this).prop("checked") == true) {
                        correct = $("input[type=text]", this).val();
                    }
                }
            });
            task["assignment"] = $("input", taskDiv).val();
            task["choices"] = choices;
            task["correct"] = correct;

            if (choices.length == 0) {
                AddError(task, "Úloha musí mať aspoň jednu neprázdnu možnosť.");
                success = false;
            } else if (correct == null) {
                AddError(task, "Úloha musí mať spávnu možnosť.");
                success = false;
            }
        }
    }
    if ($("#test_name").val() == "") {
        $("#test_name_error").html("Názov testu nesmie byť prázdny.");
        success = false;
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
    $("#test_name_error").html("");
}