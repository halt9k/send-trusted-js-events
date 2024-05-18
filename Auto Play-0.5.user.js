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


function log_ex(message, loc) {
	const sourceUrl = `${loc.origin}${loc.pathname}`;
    const log_exMessage = `%c${message} %c@${sourceUrl}`;
    console.log(log_exMessage, 'color: blue;', 'color: green;');
}


function get_square_size()
	{
	let board = document.querySelectorAll("cg-board")[0];
	return {'x': board.clientWidth / 8, 'y': board.clientHeight / 8}
	}


function try_get_relative_pos(elem)
	{
	let tr = unsafeWindow.getComputedStyle(elem).transform;
	let mat = new WebKitCSSMatrix(tr);

	let xy = {x: mat.m41, y: mat.m42};
	return xy;
	}


function try_get_board_square(elem)
	{
	let pos_px = try_get_relative_pos(elem)
	let sz = get_square_size();
	let pos = {x: pos_px.x / sz.x, y: pos_px.y / sz.y}

	if (Number.isInteger(pos.x) && Number.isInteger(pos.y))
		return pos
	else
		return undefined
	}


function getScreenPosPx(elem, posAtMiddle){
	// Returns absolute position in pixels (px) relative to screen corner
	// Works at least on W10 Firefox

	let rect = elem.getBoundingClientRect();
	let screen_scale = window.devicePixelRatio;

	// relative to page corner
	// (not from window corner, skips window menu area)
	let elem_x_px = (posAtMiddle? (rect.left + rect.right) / 2 : rect.x) * screen_scale;
	let elem_y_px = (posAtMiddle? (rect.bottom + rect.top) / 2 : rect.y) * screen_scale;

	// page corner relative to screen corner
	let page_x_px = window.mozInnerScreenX * screen_scale;
	let page_y_px = window.mozInnerScreenY * screen_scale;
	// cross-platform closet guesss, hacky and bad
	// expects borders of same width and no page footer at all
	// let page_x = (window.screenX + (window.outerWidth - window.innerWidth)/2) * screen_scale;
	// let page_y = (window.screenY + (window.outerHeight - window.innerHeight)) * screen_scale;

	debugger;

	let screen_x = Math.round(page_x_px + elem_x_px);
	let screen_y = Math.round(page_y_px + elem_y_px);

	return {x:screen_x, y:screen_y}
}


function get_screen_pos_randomized(elem){
	let xy = getScreenPosPx(elem, true);

	let x = getRandomInt(xy.x - 5, xy.x + 5);
	let y = getRandomInt(xy.y - 5, xy.y + 5);

	return {x: x, y: y}
}


function get_relative_pos_randomized(elem) {
	// returns relative position of the element
	let rct = try_get_relative_pos(elem);
	let x = getRandomInt(rct.x + 5, rct.x + elem.offsetWidth - 5);
	let y = getRandomInt(rct.y + 5, rct.y + elem.offsetHeight - 5);
	return {x:x, y:y}
}


function press_on_board(elem, x, y) {
	var board = document.querySelector('.cg-wrap > cg-container:nth-child(1) > cg-board:nth-child(1)');
	var md = new Event('mousedown', {button: 0, clientX: x, clientY: y, layerX: x, layerY: y, target: board});
	board.dispatchEvent(md)
	var mu = new Event('mouseup', {button: 0, clientX: x, clientY: y, layerX: x, layerY: y, target: board});
	board.dispatchEvent(mu)
}


function click_board_element(elem)
	{
	let pos = get_relative_pos_randomized(elem)

    pos = try_get_board_square(elem);
	if (!pos)
		return;

	log_ex('click on: ' + pos.x + ' ' + pos.y, location)
	let xy = get_screen_pos_randomized(elem)
	document.title = "auto_click " + xy.x + ' ' + xy.y;

	// Unfinished, press still not happening, trusted?
	// press_on_board(elem, pos.x, pos.y);
	}


function detect_player_side()
	{
	if (side !== 0)
		{return}

	log_ex('side unknown', location)

	// let ghost = document.getElementsByClassName('ghost')[0];
	// if (ghost.length > 0)

	let ghost = document.querySelector(".cg-wrap")
	if (ghost)
		{
		if (ghost.className.includes('white'))
			{side = 1}
		if (ghost.className.includes('black'))
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
	click_board_element(elem);
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
	// log_ex('gnf max ' + highest_weight, location)
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
			// log_ex('thr ' + thr, location)
			return elem;
			}
		}

	}


function TrySelect()
	{
	if (my_pieces.length > 0)
		{
		// log_ex('clicking_random_piece', location)

		let elem = TryPrioritySelect();
		if (!elem)
			{elem = TryPrioritySelect()}

		if (!elem)
			{
			// log_ex('prob selection failed', location)
			let movedestN = getRandomInt(0, my_pieces.length - 1)
			elem = my_pieces[movedestN];
			}

		TryDeclareSelect(elem);
		}
	}


function UpdateStates()
	{
	// log_ex('Updated', location);
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

	// log_ex(board_squares, location);
	for (const pce of all_pieces){
		let pos = try_get_board_square(pce);
		if (!pos)
			continue

		// pce.classname
		// log_ex(pos, location);
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

	// log_ex('clicking_random_dest', location);
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
	click_board_element(click_target);

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

	// log_ex(board_squares, location)

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

	log_ex('open_new_tab', location)

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


var auto_play_start_time
async function run_loop()
	{
    try_move_new_tab()

    log_ex('run_loop', location)

	auto_play_start_time = new Date()

	try_mute()
	for (let i = -5; i < 5000; i++)
		{
		if (!check_opponent(auto_play_start_time))
			window.close()


		await sleep(Math.pow(i, 1.7) * 200 )
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


log_ex('Adding event listener', location)
document.addEventListener('keyup', doc_keyUp, false);


function is_maximized() {
    var is_max = screen.availWidth - window.innerWidth === 0;
	log_ex('is_max: ' + is_max, location);
	return is_max;
}


function query_selector(selector, debug_msg=true) {
	var btn = document.querySelector(selector);
	if (debug_msg && !btn)
		log_ex("Button not found: " + selector, location)
	return btn
}


function press_by_selector(selector, event) {
	var btn = query_selector(selector);
	if (!btn)
		return;

	var md_event = new Event('mousedown', {'bubbles': true, 'cancelable': true});
	btn.dispatchEvent(md_event)
}


function click_btn(selector) {
	var btn = query_selector(selector);
	if (!btn)
		return;
	btn.click()
}


async function auto_create_new_game() {
	if (document.URL != "https://lichess.org/")
		return;
	if (is_maximized())
		return;

	await sleep(250)

	// press_by_selector("button.button.button-metal.config_hook", 'mousedown');
	press_by_selector("button.button:nth-child(1)", 'mousedown');
	await sleep(400)
	click_btn("button.color-submits__button:nth-child(2)");
}
auto_create_new_game()


function is_game_page() {
	return document.URL.match('https://lichess.org/[a-z].*') == document.URL;
}


var dummy_test_start_time
async function auto_start_dummy() {
	if (is_maximized())
		return;
	if (!is_game_page)
		return;

	log_ex("Testing for dummy", location)


	dummy_test_start_time = new Date()

	await sleep(250)
	// press_by_selector("button.button.button-metal.config_hook", 'mousedown');
	press_by_selector("button.button:nth-child(1)", 'mousedown');
	await sleep(400)
	click_btn("button.color-submits__button:nth-child(2)");
}
auto_start_dummy()


