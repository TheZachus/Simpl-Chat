const Message () {
    return <div>Message Component</div>;
};

const Button (title, redirect) {
    return <button>{title}</button>;
};

const InputBar () {
    return <form>
    <input type="text" placeholder="Type a message..." />
    <button type="submit">Send</button>
    </form>>;
}

const SearchBar () {
    return <div>Search Bar Component</div>;
};

const ChatList () {
    return <div>Chat List Component</div>;
};

export { Message, Button, InputBar, SearchBar, ChatList };

ChatEmissionListeners () {
 return <div>Chat Emission Listeners Component</div>;
};