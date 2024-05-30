// ==UserScript==
// @name         Send trusted input example
// @namespace    http://tampermonkey.net/
// @version      0.2
// @description  try to take over the world!
// @author       You
// @icon         data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==
// @match        https://www.google.com
// @grant unsafeWindow
// @grant window.close
// @grant window.focus
// @grant window.onurlchange
// @grant GM_openInTab
// @grant GM_registerMenuCommand
// @run-at  context-menu
// @run-at  page-load
// ==/UserScript==

// require http://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js
// require https://gist.github.com/raw/2625891/waitForKeyElements.js

const CSS_SEL_GOOGLE_SEARCH = "div.RNNXgb"
const CSS_SEL_GOOGLE_SEARCH_BTN = "input.gNO89b"
const REQ_CLICK = 'REQ CLICK ${X} ${Y}'
const REQ_KEYS = 'REQ KEYS ${K}'
const DONE = 'DONE'


function log_ex(message, loc) {
	const sourceUrl = `${loc.origin}${loc.pathname}`;
    const log_exMessage = `%c${message} %c@${sourceUrl}`;
    console.log(log_exMessage, 'color: blue;', 'color: green;');
}


function getClientPosPx(elem, posAtMiddle){
	// Returns approximate position in pixels (px) relative to window corner

	let rect = elem.getBoundingClientRect();
	let screen_scale = window.devicePixelRatio;

	// relative to page corner
	// (not from window corner, skips window menu area)
	let elem_x_px = (posAtMiddle? (rect.left + rect.right) / 2 : rect.x) * screen_scale;
	let elem_y_px = (posAtMiddle? (rect.bottom + rect.top) / 2 : rect.y) * screen_scale;

	// page corner relative to window corner
	let page_x_px = (window.outerWidth - window.innerWidth)/2 * screen_scale;
	let page_y_px = (window.outerHeight - window.innerHeight) * screen_scale;

	let x = Math.round(page_x_px + elem_x_px);
	let y = Math.round(page_y_px + elem_y_px);

	return {x:x, y:y}
}


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


async function waitUntilDone() {
	for (let i = 0; i < 5000; i++)
		{
		await sleep(200)
        if (document.title == DONE)
            return;
		}
}


function trustedClick(elem)
	{
	let xy = getClientPosPx(elem, true)
	document.title = REQ_CLICK.replace('${X}', xy.x).replace('${Y}', xy.y);
    waitUntilDone();
	}


function trustedKeys(elem, keys)
	{
	elem.focus()
	document.title = REQ_KEYS.replace('${K}', keys);
    waitUntilDone();
	}


async function main()
	{
    log_ex('run_loop', location)

    let search = document.querySelector(CSS_SEL_GOOGLE_SEARCH)
	trustedClick(search)
    trustedKeys(search, 'H e l l o W o r l d')
    let btn = document.querySelector(CSS_SEL_GOOGLE_SEARCH_BTN)
    trustedClick(btn)
	}
main()

