

function get_sessions() {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", "http://127.0.0.1:8000/sessions");
    xhr.send();
    xhr.responseType = "json";
    xhr.onload = () => {
        if (xhr.readyState == 4 && xhr.status == 200) {
            const data = xhr.response;
            render_users(data);
        } else {
            console.log(`Error: ${xhr.status}`);
        }
    };
}

function render_users(users) {
    users = users['sessions'];
    const userContainer = document.getElementsByClassName('panelContent')[0];
    const userTemplate = document.getElementById('user-template');

    userContainer.innerHTML = '';

    users.forEach(itemData => {
        const newItem = document.importNode(userTemplate.content, true);

        let name = itemData.name;
        const capitalize =
            name.charAt(0).toUpperCase()
            + name.slice(1)

        newItem.querySelector('button').textContent = capitalize;
        //newItem.querySelector('p').textContent = itemData.itemDescription;

        userContainer.appendChild(newItem);
    });
}

window.onload = function() {
    get_sessions();
};