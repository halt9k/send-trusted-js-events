// ==UserScript==
// @name         Auto Play
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @icon         data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==
// @match        https://lichess.org/*
// @match        https://wiki.greasespot.net/*
// @grant unsafeWindow
// @grant debug
// @grant window.close
// @grant window.jQuery
// @grant window.focus
// @grant window.onurlchange
// @grant GM_openInTab
// @grant GM_registerMenuCommand
// @require http://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js
// @require https://gist.github.com/raw/2625891/waitForKeyElements.js
// @run-at  context-menu
// @run-at  page-load
// ==/UserScript==

var side = 0;
var last_selected_value = 0
var board_squares = Array.from(Array(8), () => [null, null, null, null, null, null, null, null])
var board_squares_weights
var last_target_pos = {x: 0, y: 0}
var my_pieces, all_pieces
var move_info
var startTime
const CSS_SEL_OPPONENT_LEFT = ".ruser-top > i:nth-child(1)"


function try_mute()
	{
	// lichess.sound.setVolume(0);
    document.querySelectorAll('audio, video').forEach(item => {
        item.muted = true;
        item.pause();
    });
	}

//mousedown { target: cg-board, buttons: 1, clientX: 824, clientY: 289, layerX: 67, layerY: 249 }
//clickEvent.initMouseEvent('mousedown', false, false, unsafeWindow, 0, 883, 300, 180, 120, false, false, false, false, 1, null);


function get_square_size()
	{
	let board = document.querySelectorAll("cg-board")[0];
	return board.clientWidth / 8
	}


function try_get_board_square(elem)
	{
	let tr = unsafeWindow.getComputedStyle(elem).transform;
	let mat = new WebKitCSSMatrix(tr);

	let sz = get_square_size();
	let pos = {x: mat.m41 / sz, y: mat.m42 / sz}

	if (Number.isInteger(pos.x) && Number.isInteger(pos.y))
		return pos
	else
		return undefined
	}


function declare_click(elem)
	{
	//GM_openInTab(document.url)
	let client_x = unsafeWindow.mozInnerScreenX;
	let client_y = unsafeWindow.mozInnerScreenY;

	debugger
	let rct = elem.getBoundingClientRect();
	let x = getRandomInt(rct.left + 5, rct.right - 5) + client_x;
	let y = getRandomInt(rct.top + 5, rct.bottom - 5) + client_y;
	let scale = unsafeWindow.devicePixelRatio;
	document.title = "auto_click " + Math.round(x * scale) + ' ' + Math.round(y * scale);
    let pos = try_get_board_square(elem);
	if (!pos)
		return

	unsafeWindow.console.log('pos: ' + pos.x + ' ' + pos.y)
	}


function detect_player_side()
	{
	if (side !== 0)
		{return}

	unsafeWindow.console.log('side unknown')

	let ghost = document.getElementsByClassName('ghost');
	if (ghost.length > 0)
		{
		if (ghost[0].className.includes('white'))
			{side = 1}
		if (ghost[0].className.includes('black'))
			{side = -1}
		}
	UpdateStates()
	}



function is_opponent_active(){
	try{
        return document.querySelectorAll(CSS_SEL_OPPONENT_LEFT)[0].title != "Left the game"
    }
    catch{
        return true
    }
}


var last_alive = new Date()
function check_opponent(start_time){
	if (is_opponent_active()){
		last_alive = new Date()
		return true
	}

	var cutTime = new Date()
	var inactiveTime = (cutTime.getTime() - last_alive.getTime()) / 1000
	var timeFromStart = (cutTime.getTime() - start_time.getTime()) / 1000

	if (timeFromStart < 10 && inactiveTime > 5)
		return false

	return inactiveTime < 2

}


function GetPieceValue(elem)
	{
	let short_name = elem.className.replace("black ", "").replace("white ", "");
	switch (short_name)
		{
		case 'pawn':
			return 1;
		case 'knight':
			return 3;
		case 'bishop':
			return 4;
		case 'rook':
			return 5;
		case 'king':
			return 8;
		case 'queen':
			return 8;
		default:
			return 1;
		}
	}

function IsEnemy(elem)
	{
	if (side === 0)
		{return false;}

	let b = (side === -1 && elem.className.includes('white'));
	let w = (side === 1 && elem.className.includes('black'));
	return (b || w);
	}


function TryDeclareSelect(elem)
	{
	declare_click(elem);
	last_selected_value = GetPieceValue(elem);
	last_target_pos = try_get_board_square(elem)

	if (board_squares_weights && last_target_pos)
		{board_squares_weights[last_target_pos.x][last_target_pos.y] *= 0.3}
	}


function TryPrioritySelect()
	{
	if (!board_squares_weights)
		{return;}

	let highest_weight = 0;
	for (const piece of my_pieces)
		{
		let pos = try_get_board_square(piece);
		if (!pos)
			continue

		let dng = board_squares_weights[pos.x][pos.y];
		highest_weight = Math.max(highest_weight, dng);
		}
	// unsafeWindow.console.log('gnf max ' + highest_weight)
	// console.table(board_squares_weights)
	//move_info

	if (highest_weight === 0)
		return

	for (let I = 0; I < my_pieces.length; I++)
		{
		let movedestN = getRandomInt(0, my_pieces.length - 1)
		let elem = my_pieces[movedestN];

		let pos = try_get_board_square(elem);
		if (!pos)
			continue

		let dng = board_squares_weights[pos.x][pos.y];
		let thr = 0.1 + dng / highest_weight;


		if (Math.random() < thr)
			{
			unsafeWindow.console.log('thr ' + thr)
			return elem;
			}
		}

	}


function TrySelect()
	{
	if (my_pieces.length > 0)
		{
		// unsafeWindow.console.log('clicking_random_piece')

		let elem = TryPrioritySelect();
		if (!elem)
			{elem = TryPrioritySelect()}

		if (!elem)
			{
			// unsafeWindow.console.log('prob selection failed')
			let movedestN = getRandomInt(0, my_pieces.length - 1)
			elem = my_pieces[movedestN];
			}

		TryDeclareSelect(elem);
		}
	}


function UpdateStates()
	{
	unsafeWindow.console.log('Updated');
	board_squares = Array.from(Array(8), () => [null, null, null, null, null, null, null, null]);
	board_squares_weights = Array.from(Array(8), () => [1, 1, 1, 1, 1, 1, 1, 1]);

	let whites = document.querySelectorAll("piece.white:not(piece.ghost)");
	let blacks = document.querySelectorAll("piece.black:not(piece.ghost)");
    all_pieces = document.querySelectorAll("piece.white:not(piece.ghost),piece.black:not(piece.ghost)");

    my_pieces = all_pieces;
	if (side === -1)
        my_pieces = blacks;
	if (side === 1)
        my_pieces = whites;

	// unsafeWindow.console.log(board_squares);
	for (const pce of all_pieces){
		let pos = try_get_board_square(pce);
		if (!pos)
			continue

		// pce.classname
		// unsafeWindow.console.log(pos);
		board_squares[pos.x][pos.y] = pce;
		if (IsEnemy(pce))
			{AddDanger(pos)}
	}
	if (last_target_pos)
		board_squares_weights[last_target_pos.x][last_target_pos.y] += 4
	}



var could_move = false
function TryMove(board_squares)
	{
	let places = document.getElementsByClassName("move-dest");

	let can_move = (places.length !== 0)
	if (could_move !== can_move)
		{
		if (!could_move)
			UpdateStates();

		could_move = can_move;
		}

	if (!can_move)
		return false;

	// unsafeWindow.console.log('clicking_random_dest');
	let click_target
	if (last_selected_value < 5)
		{
		for (const place of places)
			{
			let pos = try_get_board_square(place);
			if (!pos)
				continue

			let loc = board_squares[pos.x][pos.y]
			if (loc && IsEnemy(loc) && Math.random > 0.2)
				{
				click_target = place
				break;
				}
			}
		}

	if (last_selected_value >= 5 || !click_target)
		{
		let movedestN = getRandomInt(0, places.length - 1);
		click_target = places[movedestN];
		}
	declare_click(click_target);

	return true;
	}


function AddDanger(pos)
	{
	for (let x = -2; x <= 2; x++)
		{
		for (let y = -2; y <= 2; y++)
			{
			if (x === 0 && y === 0)
				continue;

			let xx = x + pos.x;
			let yy = y + pos.y;
			if (xx >= 0 && xx < 8 && yy >= 0 && yy < 8)
				{
				board_squares_weights[xx][yy] += (4 - x * x) + (4 - y * y);
				}
			}
		}
	}


function MakeRandomMove()
	{
	move_info = '';
	detect_player_side();
    UpdateStates();

	// unsafeWindow.console.log(board_squares)

	if (TryMove(board_squares))
		return;
	TrySelect();
	}


function getRandomInt(min, max)
	{
	return Math.floor(Math.random() * (max - min + 1) + min);
	}


function try_move_new_tab(){
    if ($(window).width() < 400 || $(window).height() < 400)
		return

	unsafeWindow.console.log('open_new_tab')

	let left = screen.width - 300
	let windowFeatures = "width=300,height=400,left=" + left + ",top=0"

	let wnd = window.open(window.location.href, "_blank", windowFeatures)

	if (wnd){
		window.open("https://lichess.org/", "")
		window.close()
    }
}



function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}



async function run_loop()
	{
    try_move_new_tab()

    unsafeWindow.console.log('run_loop')

	startTime = new Date()

	try_mute()
	for (let i = -5; i < 5000; i++)
		{
		if (!check_opponent(startTime))
			window.close()


		await sleep(Math.pow(i, 1.5) * 50)
		MakeRandomMove()
		}
	}


function doc_keyUp(e) {
    switch (e.keyCode) {
        case 82:
            //r, not s, not m
            run_loop();
            break;
        default:
            break;
    }
}


unsafeWindow.console.log('Adding event listener')
document.addEventListener('keyup', doc_keyUp, false);
