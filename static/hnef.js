const ROW = 11;
const COLUMN = 11;
const SPACE_SIZE = 40;


function init(){
    // SELECT CANAVS
    const canvas = document.getElementById("board");
    const ctx = canvas.getContext("2d");

    function drawBoard(){
	for(let i = 0; i < ROW; i++){
	    for(let j = 0; j < COLUMN; j++){
		// draw the spaces
		ctx.strokeStyle = "#000";
		ctx.strokeRect(j * SPACE_SIZE, i * SPACE_SIZE, SPACE_SIZE, SPACE_SIZE);
	    }
	}
    }
    drawBoard();
    //    $.getJSON('https://hnefatafl.wl.r.appspot.com/starting_board', function(result){
    $.getJSON('/starting_board', function(result){
	    console.log(result);
	    for(let i = 0; i < ROW; i++){
		for(let j = 0; j < COLUMN; j++){
		    // draw the pieces
		    if (result[i][j] == 1) {
			ctx.fillStyle = "#000";
		    } else if (result[i][j] == 2) {
			ctx.fillStyle = "#EED";
		    }
		    if (result[i][j] != 0) {
			ctx.beginPath();
			ctx.arc(
				(j * SPACE_SIZE) + SPACE_SIZE/2,
				(i * SPACE_SIZE) + SPACE_SIZE/2,
				SPACE_SIZE/2, 
				0, 
				2 * Math.PI);
			ctx.fill();
			ctx.stroke();
		    }
		}
	    }
	});
}
init();