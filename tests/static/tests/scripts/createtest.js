
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
        "class": "task",
        "id": generateDomID()
    });
    $("<input>", {
        "type": "text",
    }).val(task.assignment).appendTo(taskDiv);
    renderRemoveButton().appendTo(taskDiv);
    return taskDiv;
}

function renderChoiceTask(task) {
    var taskDiv = $("<div>", {
        "class": "task",
        "id": generateDomID()
    });
    $("<input>", {
        "type": "text",
    }).val(task.assignment).appendTo(taskDiv);
    renderRemoveButton().appendTo(taskDiv);
    var choicesDiv = $("<div>", {"class": "choices"}).appendTo(taskDiv);
    if (task["choices"].length == 0) {
        renderChoice("choice_" + taskDiv.attr("id")).appendTo(choicesDiv);
    } else {
        for (var choice in task["choices"]) {
            renderChoice("choice_" + taskDiv.attr("id"), task["choices"][choice], task["choices"][choice]==task["correct"]).appendTo(choicesDiv);
        }
    }
    $("<button>", {"class": "add_choice"}).click(function() {
        renderChoice("choice_" + taskDiv.attr("id"), choice).appendTo(choicesDiv);
    }).html("pridat moznost").appendTo(taskDiv);
    return taskDiv;
}

function renderChoice(name, content = "", checked = false) {
    var choiceDiv = $("<div>", {"class" : "choice"});
    $("<input>", {"type": "radio", "name": name}).prop("checked", checked).appendTo(choiceDiv);
    $("<input>", {"type": "text"}).val(content).appendTo(choiceDiv);
    $("<button>", {"class": "delete_choice"}).html("X").click(function() {
        $(this).parent().remove();   
    }).appendTo(choiceDiv);
    return choiceDiv;
}

function renderRemoveButton() {
    var removeButton = $("<button>", { "class": "delete_task" }).append("X").click(function (el) {
        var taskDiv = $(el.target).parent();
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
    return success;
}

function AddError(task, error) {
    var errorDiv = $("#" + task["dom_id"] + " .errors");
    if (errorDiv.html() != "") {
        errorDiv.append("<br />");
    }
    errorDiv.append(error);
}

function ResetErrors() {
    for (var task in tasks) {
        $("#" + task + " .errors").empty();
    }
}