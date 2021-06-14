const messengerForm = get('.msger-inputarea'),
messengerInput = get('.msger-input'),
messengerChat = get('.msger-chat'),
time = get('.msg-info-time');

time.innerText=setDate();

const BOT_IMG = "https://image.flaticon.com/icons/svg/327/327779.svg";
const PERSON_IMG = "https://image.flaticon.com/icons/svg/145/145867.svg";
const BOT_NAME = "U.Buddy Bot";
const PERSON_NAME = "You";


messengerForm.addEventListener("submit", event => {
    event.preventDefault();

    const msgText = messengerInput.value;
    if (!msgText) return;

    appendMessage(PERSON_NAME, PERSON_IMG, "right", msgText);
    messengerInput.value = "";
    botResponse(msgText)
  });

function appendMessage(name, img, side, text, links) {
         let imagesOrLinks = ''
         if(links) {
             let websites = links['websites'],
             images = links['image'];
             if(images) {
                for(let index in images) {
                    imagesOrLinks = imagesOrLinks + '<img src="' + images[index] + '" class="images"><br>'
                }
            }
            if(websites) {
                for(let index in websites) {
                    imagesOrLinks = imagesOrLinks + '<br><a href="' + websites[index]['link'] + '">' + websites[index]['text'] + '</a><br>'
                }
            }
         }
            const msgHTML = `
        <div class="msg ${side}-msg">
        <div class="msg-img" style="background-image: url(${img})"></div>

        <div class="msg-bubble">
        <div class="msg-info">
            <div class="msg-info-name">${name}</div>
            <div class="msg-info-time">${setDate()}</div>
        </div>

        <div class="msg-text">${text}</div> ` + imagesOrLinks + `

        </div>
        </div>
        `;

        messengerChat.insertAdjacentHTML("beforeend", msgHTML);
        messengerChat.scrollTop += 500;
  }

function setDate() {
    let date = new Date();
    hours = date.getHours();
    amPm = "";
    if(hours > 12) {
        hours = hours - 12
        amPm = "pm"
    } else {
        amPm = "am"
    }
    return hours + ":" + date.getMinutes() + " " + amPm;
}

function botResponse(rawText) {

    $.get("/getResponse", { msg: rawText }).done(function (data) {
      console.log(rawText);
      console.log(data);
      const msgText = data;
      if(msgText['links']) {
        appendMessage(BOT_NAME, BOT_IMG, "left", msgText['response'], msgText['links'][0]);
      } else {
        appendMessage(BOT_NAME, BOT_IMG, "left", msgText['response'], null);
      }

    });
  }


  function get(selector, root = document) {
    return root.querySelector(selector);
  }