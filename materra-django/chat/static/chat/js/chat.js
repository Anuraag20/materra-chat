const user_id = parseInt($('#user-id').val())
const this_username = $('#username').val()
const chatList = $('#chats')
const messageWindow = $('#messageWindow')
const memberNames = JSON.parse(localStorage.getItem('memberNames') ? localStorage.getItem('memberNames'): '{}') 
const ws = new WebSocket(`/ws/user/${user_id}/`);
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

var aiTexts = []
var currentRoom = null		    

const createMessageDOMObject = async (message) => {
	
	let senderId = message['sender_id']
	let name = senderId == user_id ? 'You': await getMemberNameById(message['sender_id'], message['conversation_id'])
	let file = message['file']
	let content = message['content']
	if (file){
		content = `File: <a href='${file}'>${file}</a><br/>` + content
	}
	return `<div class="mb-2"><strong>${name}:</strong> ${content}</div>`
}

const createConversationDOMObject = (conversation) => {
	return `<div 
	    onclick="renderRoom('${conversation.id}')" 
	    class="list-group-item"
	    id="${conversation.id}"
	    data-admin="${conversation.is_admin ? 1: 0}"
	>${conversation.name}</div>`
}

const getMembers = async (conversation_id) => {
	var response = await fetch(`/api/chat/get-members/${conversation_id}`)
	if (!response.ok){
		alert('something went wrong...')
	}
	response = await response.json()
	for (const [key, value] of Object.entries(response)) {
	  	memberNames[key] = value
	}
	localStorage.setItem('memberNames', JSON.stringify(memberNames))
}

const getMemberNameById = async (member_id, conversation_id) => {
	if (memberNames == {} || memberNames[member_id] === undefined) await getMembers(conversation_id)
	return memberNames[member_id]
}

const renderRoom = async (id) => {
	if (currentRoom == id){
		return 
	}
	
	currentRoom = id
	$('#send').attr('disabled', false)
	var html = ''

	if (currentRoom != 'AIASSISTANT'){
		messages = await getNewMessages(id)
		if ($(`#${id}`).data('admin') == 1){
			html += "<button onclick='archiveConversation()'>Archive Conversation</button>"
		}
		for (const message of messages){
			html+=await createMessageDOMObject(message)
		}

	}

	messageWindow.html(html)
}

const archiveConversation = async () => {
	var response = await fetch(`/api/chat/archive-conversation/${currentRoom}`)
	if (!response.ok){
		alert('something went wrong...')
	}
}
const getConversations = async () => {

	var response = await fetch(`/api/chat/get-conversations/`)
	if (!response.ok){
		alert('something went wrong...')
	}
	response = await response.json()
	var html = ''
	response.forEach((conversation) => {
		html += createConversationDOMObject(conversation)	
	})
	chatList.html(html)


}
const createRoom = async () => {
	let usernamesInput = $("[name='usernames']")
	let name = $("[name='room-name']")
	let usernames = usernamesInput.val().split(',').map((name) => name.trim().replace(/ /gi, '-')).concat(this_username)
	
	const request = new Request('/api/chat/create-room', {
		method: 'POST',
		headers: {
			'X-CSRFToken': csrftoken,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			users: usernames,
			conversation_name: name.val()			
		}),
		mode: 'same-origin' 	
	});

	let response = await fetch(request)
	if (!response.ok){
		alert('something went wrong...')
	}
	usernamesInput.val('')
	name.val('')
}

const getCacheData = (key, type = Array) => {
	let data = localStorage.getItem(key)
	if (data !== null){
		return JSON.parse(data)
	}
	return new type()
}


const getOldMessages = async (id) =>{
	let key = `chatMessages${id}`
	let cachedMessages = getCacheData(key)
	
	let before = cachedMessages.length !== 0 ? cachedMessages[0].created_at: ''
	var response = await fetch(`/api/chat/get-messages/${id}?before=${before}`)
	if (!response.ok){
		alert('something went wrong...')
		return
	}
	response = await response.json()
	//localStorage.setItem(key, JSON.stringify(response.data.concat(cachedMessages)))
	return response
}

const getNewMessages = async (id) => {
	
	let key = `chatMessages${id}`
	let cachedMessages = getCacheData(key)
	let after = cachedMessages.length !== 0? cachedMessages[cachedMessages.length - 1].created_at: ''
	var response = await fetch(`/api/chat/get-messages/${id}?after=${after}`)
	if (!response.ok){
		alert('something went wrong...')
		return
	}
	response = await response.json()
	//localStorage.setItem(key, JSON.stringify(cachedMessages.concat(response.data)))
	return response
}

const createEnquiry = async () => {
	const request = new Request('/api/enquiry/create', {
		method: 'POST',
		headers: {
			'X-CSRFToken': csrftoken,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			user_id: user_id	
		}),
		mode: 'same-origin' 	
	});

	let response = await fetch(request)
	if (!response.ok){
		alert('something went wrong...')
	}

}

ws.onmessage = async (message) => {
	message = JSON.parse(message.data)
	let data = message.data
			console.log(data)
	if (message['type'] == 'broadcast_message'){
		if (data['conversation_id'] == currentRoom){
			messageWindow.append(await createMessageDOMObject(data))
		} else {
			//Caching logic
		}
	} else if (message['type'] == 'new_conversation'){
		chatList.prepend(createConversationDOMObject(data))
	} else if (message['type'] == 'archive_conversation'){
		if (currentRoom == data['id']){
			messageWindow.html('The current conversation has been archived!')
			$('#send').attr('disabled', true)
		} 
		$(`#${data['id']}`).remove()
	}


}

$('#start-chat').on('click', createRoom)
$('#create-enquiry').on('click', createEnquiry)

$('#send').on('click', async () => {
	if (currentRoom == 'AIASSISTANT'){
		aiTexts.push({
			"role": "user",
			"content": $('#message-content').val()
		})
		messageWindow.append(`<div class="mb-2"><strong>You:</strong> ${$('#message-content').val()}</div>`)
		messageWindow.append('<div class="mb-2"><strong>AI:</strong></div>')

		const request = new Request('http://localhost:8001', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
			body: JSON.stringify(aiTexts)

			});
		var content = ''
		fetch(request).then((response)=>{
				const reader = response.body.getReader();
				reader.read().then(function pump({ done, value }) {
				if (done) {
					aiTexts.push({
						"role": "assistant",
						"content": content
					})
				return;
				}
				var text = new TextDecoder("utf-8").decode(value);
				content += text
				messageWindow.find("div:last").remove()
				messageWindow.append(`<div class="mb-2"><strong>AI:</strong> ${content}</div>`)
				return reader.read().then(pump);
         	 	})
		});

	} else{
		let file = $('#chat-file').prop('files')
		let message = $('#message-content').val()
		if (file.length != 0) {
			let formData = new FormData()
			formData.append('file', file[0])
			formData.append('message', message)
			const request = new Request(`/api/chat/upload-file/${currentRoom}`, {
				method: 'POST',
				headers: {
					'X-CSRFToken': csrftoken
				},
				body: formData,
				mode: 'same-origin' 	
			})

			var response = await fetch(request)
			if (!response.ok){
				alert('something went wrong...')
			}
			$('#chat-file').val('')
		} else {
			ws.send(JSON.stringify({
				'type': 'new_message',
				'data': {
					'conversation': currentRoom,
					'message': message
				}
			}))
		}
	}
	$('#message-content').val('')
})

$(document).ready(()=>getConversations())

/*
	* Keep read-receipts implementation for later!
	* If there is nothing in the local storage:
	* 1. Load all coversations (paginate - top 10 most recent messages)
	* 2. On click, just load top 10 most recent 
	*
	* If there is something in the local storage:
	* 1. Render all conversations in local storage
	* 2. Fetch top 10 most recent conversations and compare with order in local-storage
	* 3. Re-arrange accordingly
	* 4. On click of a conversation, load the top 10 most recent
*/
