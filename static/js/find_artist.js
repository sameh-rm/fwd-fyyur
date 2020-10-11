var input = document.getElementById("search_artist");
var $resultList = $("#result_list");
var $searchBox = $("#search-box");
$searchBox.hover(
	() => $resultList.show(),
	() => $resultList.hide()
);
$resultList.hide();

input.addEventListener(
	"input",
	function (event) {
		// if (event.code === "Enter" || event.code == "NumpadEnter") {
		$resultList.empty();

		console.log(input.value);
		if (event.target.value !== "") {
			fetch("/artists/search_json", {
				method: "POST",
				body: JSON.stringify({
					search_term: input.value,
				}),
				headers: {
					"Content-Type": "application/json",
				},
			})
				.then((res) => res.json())
				.then((jsonRes) => {
					jsonRes.data.forEach((artist) => {
						$resultList.append(createRow(artist));
					});
				})
				.catch((error) => console.error(error));
		} else {
			$resultList.empty();
			$resultList.hide();
		}

		event.preventDefault();
	}
	// }
);

function createRow(artist) {
	var rowEl = document.createElement("div");
	rowEl.className = "row";

	var cardWrapperEl = document.createElement("a");
	cardWrapperEl.className = "col-xs-12 recent-card";
	cardWrapperEl.href = artist.absoluteURL;

	var imgContainerEl = document.createElement("div");
	imgContainerEl.className = "col-xs-4 img-container";

	var imgEl = document.createElement("img");
	imgEl.className = "img-responsive recent-img";
	imgEl.src = artist.image_link;

	var cardBodyContainerEl = document.createElement("div");
	cardBodyContainerEl.className = "col-xs-8";

	var cardBodyEl = document.createElement("div");
	cardBodyEl.className = "card-body";

	var cardTitleEl = document.createElement("div");
	cardTitleEl.className = "card-title";
	cardTitleEl.innerText = artist.name;

	var cardTextEl = document.createElement("div");
	cardTextEl.className = "card-text";
	cardTextEl.innerText = artist.city;

	imgContainerEl.appendChild(imgEl);
	cardWrapperEl.appendChild(imgContainerEl);
	cardBodyEl.appendChild(cardTitleEl);
	cardBodyEl.appendChild(cardTextEl);
	cardBodyContainerEl.appendChild(cardBodyEl);
	cardWrapperEl.appendChild(cardBodyContainerEl);
	rowEl.appendChild(cardWrapperEl);
	return rowEl;
}
