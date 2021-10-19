var socket = new WebSocket("ws://localhost:1234/ws/get_callers/");
var myNotificationID = null;
var callFrom = null;
var prevNum = null;
var rang = false;
var accepted = false;

socket.onmessage = function (event) {
  var data = JSON.parse(event.data);
  message = JSON.parse(data.message);
  console.log(message);
  callFrom = message.number;
  callStatus = message.status;
  // console.log(callStatus + " " + callFrom);
  // if (callStatus === "Ringing" && callFrom !== prevCallFrom) {
  if (callStatus === "Ringing" && prevNum !== callFrom) {
    rang = true; 
    prevNum = callFrom;
    chrome.notifications.create(
      "callNotifier",
      {
        type: "basic",
        iconUrl: "images/RCN.png",
        title: "Incoming Call",
        message: callFrom,
        priority: 2,
        buttons: [{ title: "Accept" }, { title: "Reject" }],
      },
      function (id) {
        myNotificationID = id;
        // console.log(id);
      }
    );
  } else if (callStatus === "Accepted") {
    rang = false;
    prevNum = null;
    accepted = false;
    chrome.notifications.clear("callNotifier");
  } else if (callStatus === "Disconnected") {
    chrome.notifications.clear("callNotifier");
    if (rang && !accepted) {
      chrome.notifications.create(
        "missedCallNotifier",
        {
          type: "basic",
          iconUrl: "images/RCN.png",
          title: "You have a missed call from",
          message: callFrom,
          priority: 2,
        },
        function (id) {
          myNotificationID = id;
          // console.log(id);
        }
      );
    }
    accepted = false;
    prevNum = null;
    rang =false;
  }
};

chrome.notifications.onButtonClicked.addListener(function (notifId, btnIdx) {
  // alert("Button clicked " + btnIdx);
  // console.log(myNotificationID + " " + notifId);
  if (notifId === myNotificationID) {
    accepted = true;
    if (btnIdx === 0) {
      callAccepted(callFrom);
      alert("You are in a call with " + callFrom);
    } else if (btnIdx === 1) {
      chrome.notifications.clear(myNotificationID);
    }
  }
});

function callAccepted(callFrom) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "http://localhost:1234/acceptCall/" + callFrom, true);
  xhr.send();
  xhr.onload = function () {
    // console.log(this.status);
    if (this.status == 200) {
      console.log(this.responseText);
    }
  };
}
