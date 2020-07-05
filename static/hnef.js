const ROW = 11;
const COLUMN = 11;
const SPACE_SIZE = 40;
const CANVAS_WIDTH = 450;
const CANVAS_HEIGHT = 450;
const ATTACKER = 1;
const DEFENDER = 2;

var canvas = document.getElementById("board");
var ctx = canvas.getContext("2d");
var mouse = { x: 0, y: 0 }

document.addEventListener('mousemove', function(e) {
	    mouse.x = e.pageX;
	    mouse.y = e.pageY;
	}, false);

function setHeader(xhr) {
    xhr.setRequestHeader("Access-Control-Allow-Origin", "*");
    }

function drawBoard(ctx){
    ctx.fillStyle = "#955";
    ctx.strokeStyle = "#000";
    for(let i = 0; i < ROW; i++){
	for(let j = 0; j < COLUMN; j++){
	    // draw the spaces
	    ctx.strokeRect(j * SPACE_SIZE, i * SPACE_SIZE, SPACE_SIZE, SPACE_SIZE);
	    ctx.fillRect(j * SPACE_SIZE, i * SPACE_SIZE, SPACE_SIZE, SPACE_SIZE);
	}
    }
}

function placePieces(ctx, result){
    console.log('redraw');
    console.log(result);
    for(let i = 0; i < ROW; i++){
	for(let j = 0; j < COLUMN; j++){
	    // draw the pieces
	    if (result[i][j] == ATTACKER) {
		ctx.fillStyle = "#000"; // should use css
	    } else if (result[i][j] == DEFENDER) {
		ctx.fillStyle = "#EED"; // should use css
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
}

var myBoard;
var player = 0; // attacker is 0 

function init(ctx){
    drawBoard(ctx);

    $.ajax({url: 'starting_board',
        type: 'GET',
	dataType: 'json',
	success: function(result) {
	    myBoard = result;
	    placePieces(ctx, result);
	    },
	error: function(result) { alert(result); },
	beforeSend: setHeader
    });

}
init(ctx);

document.getElementById('board').addEventListener('click', function() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.beginPath();
    drawBoard(ctx);
    request = {
	'player': player,
	'board': myBoard
    }
    var payload = JSON.stringify(request);

    $.ajax({
	url: 'move',
	type: 'POST',
	dataType: 'json',
	contentType: 'application/json',
	success: function(result) {
	    myBoard = result;
	    placePieces(ctx, result);
	},
        error: function(result) { alert('failure!'); console.log(result); },
	beforeSend: setHeader,
        data: payload
    });

    // switch to the next player
    if (player) {
	player = 0;
    } else {
	player = 1;
    }
}, false);



