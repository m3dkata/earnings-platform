document.addEventListener("DOMContentLoaded", function () {
    const aiAssistantButton = document.getElementById("ai-assistant-button");
    const aiAssistantPopup = document.getElementById("ai-assistant-popup");
    const closePopupButton = document.getElementById("close-popup-button");
    const aiQueryForm = document.getElementById("ai-query-form");
    const chatMessages = document.getElementById("chat-messages");
    const micButton = document.getElementById("mic-button");

    let isPopupOpen = false;
    const recognition = new (window.SpeechRecognition ||
        window.webkitSpeechRecognition)();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    function loadChatHistory() {
        return fetch("/ai/history/")
            .then((response) => {
                if (!response.ok) throw new Error("Network response was not ok");
                return response.json();
            })
            .then((data) => {
                chatMessages.innerHTML = "";
                if (data.history) {
                    data.history.forEach((message) =>
                        addMessage(message.content, message.is_user)
                    );
                    return data.history.length;
                }
                return 0;
            })
            .catch((error) => {
                console.error("Error loading chat history:", error);
                return 0;
            });
    }

    function openPopup() {
        aiAssistantPopup.classList.remove("translate-y-full");
        aiAssistantButton.classList.add("hidden");
        isPopupOpen = true;

        loadChatHistory().then((historyLength) => {
            if (historyLength === 0) {
                const suggestions = [
                    "Show me the total earnings for this month.",
                    "What are the most performed operations?",
                    "Compare this month's performance with last month.",
                ];

                let formattedResponse = document.createElement("div");
                formattedResponse.className =
                    "p-4 mt-4 rounded-lg bg-purple-50 dark:bg-purple-900/30";

                const questionsTitle = document.createElement("div");
                questionsTitle.className =
                    "mb-3 text-sm font-semibold text-purple-700 dark:text-purple-300";
                questionsTitle.textContent = "Get started with:";
                formattedResponse.appendChild(questionsTitle);

                const questionsList = document.createElement("div");
                questionsList.className = "flex flex-col gap-2";

                suggestions.forEach((question) => {
                    const questionButton = document.createElement("button");
                    questionButton.className =
                        "p-2 text-sm text-left text-purple-600 transition-colors rounded-md hover:bg-purple-100 dark:text-purple-300 dark:hover:bg-purple-800/50";
                    questionButton.textContent = question;
                    questionButton.onclick = () => {
                        document.getElementById("query-input").value = question;
                        document
                            .getElementById("ai-query-form")
                            .dispatchEvent(new Event("submit"));
                    };
                    questionsList.appendChild(questionButton);
                });

                formattedResponse.appendChild(questionsList);
                addMessage(formattedResponse);
            }
        });
    }

    function closePopup() {
        aiAssistantPopup.classList.add("translate-y-full");
        aiAssistantButton.classList.remove("hidden");
        isPopupOpen = false;

        const suggestions = document.querySelector(".suggestions-container");
        if (suggestions) {
            suggestions.remove();
        }
    }

    if (aiAssistantButton) {
        aiAssistantButton.addEventListener("click", (e) => {
            e.stopPropagation();
            openPopup();
        });
    }

    if (closePopupButton) {
        closePopupButton.addEventListener("click", () => {
            closePopup();
        });
    }

    if (aiQueryForm) {
        aiQueryForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const query = document.getElementById("query-input").value;
            if (query.trim() === "") return;

            addMessage(query, true);
            document.getElementById("query-input").value = "";
            const typingIndicator = addTypingIndicator();

            fetch("/ai/query/?query=" + encodeURIComponent(query))
                .then((response) => response.json())
                .then((data) => {
                    typingIndicator.remove();
                    if (data.error) {
                        addMessage("" + data.error);
                    } else {
                        let formattedResponse = formatResponse(data);
                        addMessage(formattedResponse);
                    }
                })
                .catch((error) => {
                    typingIndicator.remove();
                    addMessage("I do not know this! Probably you reached my limits!");
                });
        });
    }

    let isRecognizing = false;

    micButton.addEventListener("click", () => {
        if (isRecognizing) {
            recognition.stop();
            isRecognizing = false;
            micButton.innerHTML = '<i class="fa-solid fa-microphone"></i>';
            return;
        }

        recognition.start();
        isRecognizing = true;
        micButton.innerHTML = '<i class="fa-solid fa-stop"></i>';
    });

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById("query-input").value = transcript;
        document.getElementById("ai-query-form").dispatchEvent(new Event("submit"));
        micButton.innerHTML = '<i class="fa-solid fa-microphone"></i>';
    };

    recognition.onend = () => {
        isRecognizing = false;
        micButton.innerHTML = '<i class="fa-solid fa-microphone"></i>';
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        micButton.innerHTML = '<i class="fa-solid fa-microphone"></i>';
    };

    function formatResponse(data) {
        let responseContent = document.createElement("div");
        responseContent.className = "flex flex-col w-full gap-4";

        if (data.data && Array.isArray(data.data)) {
            const tableDiv = document.createElement("div");
            tableDiv.className =
                "overflow-x-auto rounded-lg shadow-sm dark:text-white ";

            const table = document.createElement("table");
            table.className = "min-w-full divide-y dark:text-white divide-slate-200";

            if (data.columns) {
                const thead = document.createElement("thead");
                const headerRow = document.createElement("tr");
                data.columns.forEach((column) => {
                    const th = document.createElement("th");
                    th.className =
                        "px-4 py-2 text-xs font-semibold tracking-wider text-left text-purple-700 uppercase bg-purple-50";
                    th.textContent = column;
                    headerRow.appendChild(th);
                });
                thead.appendChild(headerRow);
                table.appendChild(thead);
            }

            const tbody = document.createElement("tbody");
            tbody.className =
                "divide-y bg-slate-100 dark:bg-slate-800 divide-slate-200 dark:text-white";
            data.data.forEach((row, i) => {
                const tr = document.createElement("tr");
                tr.className =
                    i % 2 === 0
                        ? "bg-slate-50 dark:bg-purple-50 dark:text-white"
                        : "bg-slate-100 dark:bg-purple-100 dark:text-white";
                Object.values(row).forEach((cell) => {
                    const td = document.createElement("td");
                    td.className = "px-4 py-2 text-sm text-slate-700 whitespace-nowrap";
                    td.textContent = cell;
                    tr.appendChild(td);
                });
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);
            tableDiv.appendChild(table);
            responseContent.appendChild(tableDiv);
        }

        if (data.visualization) {
            const visDiv = document.createElement("div");
            visDiv.className = "w-full p-2 mt-2 rounded-lg shadow-sm";
            visDiv.style.minHeight = "300px";

            const layout = {
                autosize: true,
                margin: { t: 30, r: 20, b: 30, l: 40 },
                width: undefined,
                height: undefined,
                useResizeHandler: true,
                responsive: true,
            };

            const config = {
                responsive: true,
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ["lasso2d", "select2d"],
                toImageButtonOptions: {
                    format: "png",
                    filename: "chart",
                    scale: 2,
                },
            };

            visDiv.style.cssText = "width: 100%; min-height: 300px; height: 400px;";

            Plotly.newPlot(
                visDiv,
                JSON.parse(data.visualization),
                layout,
                config
            ).then(() => {
                const resizeObserver = new ResizeObserver(() => {
                    Plotly.Plots.resize(visDiv);
                });
                resizeObserver.observe(visDiv);
            });
            responseContent.appendChild(visDiv);
        }

        if (data.follow_up_questions && data.follow_up_questions.length > 0) {
            const questionsDiv = document.createElement("div");
            questionsDiv.className = "p-4 mt-4 rounded-lg bg-purple-50";

            const questionsTitle = document.createElement("div");
            questionsTitle.className = "mb-3 text-sm font-semibold text-purple-700";
            questionsTitle.textContent = "Explore further:";
            questionsDiv.appendChild(questionsTitle);

            const questionsList = document.createElement("div");
            questionsList.className = "flex flex-col gap-2";

            data.follow_up_questions.forEach((question) => {
                const questionButton = document.createElement("button");
                questionButton.className =
                    "p-2 text-sm text-left text-purple-600 transition-colors duration-200 rounded-md hover:text-purple-800 hover:bg-purple-100";
                questionButton.textContent = question;
                questionButton.onclick = () => {
                    document.getElementById("query-input").value = question;
                    document
                        .getElementById("ai-query-form")
                        .dispatchEvent(new Event("submit"));
                };
                questionsList.appendChild(questionButton);
            });

            questionsDiv.appendChild(questionsList);
            responseContent.appendChild(questionsDiv);
        }

        return responseContent;
    }

    function addTypingIndicator() {
        const indicatorDiv = document.createElement("div");
        indicatorDiv.className =
            "flex max-w-[200px] items-center space-x-2 rounded-lg bg-slate-100 p-4 dark:bg-slate-800";
        indicatorDiv.innerHTML = `
            <div class="flex space-x-1">
                <div class="h-2 w-2 animate-bounce rounded-full bg-purple-600 dark:bg-purple-400" style="animation-delay: 0s"></div>
                <div class="h-2 w-2 animate-bounce rounded-full bg-purple-600 dark:bg-purple-400" style="animation-delay: 0.2s"></div>
                <div class="h-2 w-2 animate-bounce rounded-full bg-purple-600 dark:bg-purple-400" style="animation-delay: 0.4s"></div>
            </div>
            <span class="text-sm text-purple-600 dark:text-purple-400">Thinking...</span>
        `;
        chatMessages.appendChild(indicatorDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return indicatorDiv;
    }

    function addMessage(content, isUser = false) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `mb-4 max-w-[85%] rounded-lg p-4 shadow-sm ${isUser
                ? "ml-auto bg-purple-100 text-slate-800 dark:bg-purple-900/30 dark:text-slate-200"
                : "mr-auto bg-white text-slate-800 dark:bg-slate-800 dark:text-slate-200"
            }`;

        if (content instanceof HTMLElement) {
            messageDiv.appendChild(content);
        } else if (typeof content === "object") {
            messageDiv.appendChild(formatResponse(content));
        } else {
            messageDiv.textContent = content;
        }

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
});
