// ==UserScript==
// @name         Send trusted input example
// @namespace    http://tampermonkey.net/
// @version      0.2
// @description  try to take over the world!
// @author       You
// @icon         data:image/gif;base64,R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==
// @match        https://www.google.com/
// @require      http://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js
// @grant unsafeWindow
// @grant window.close
// @grant window.focus
// @grant window.onurlchange
// @grant GM_openInTab
// @grant GM_registerMenuCommand
// @run-at  context-menu
// ==/UserScript==

// require https://gist.github.com/raw/2625891/waitForKeyElements.js

// "div.RNNXgb" ?
const CSS_SEL_GOOGLE_SEARCH = 'textarea#APjFqb.gLFyf'
const CSS_SEL_GOOGLE_SEARCH_BTN = ".FPdoLc"
const CSS_SEL_GOOGLE_SEARCH_DROPDOWN_BTN = "input.gNO89b[value='Google Search']"
const CSS_SEL_GOOGLE_LOGO = ".lnXdpd"

const REQ_CLICK = 'REQ CLICK ${X} ${Y}'
const REQ_KEYS = 'REQ KEYS ${K}'
const DONE = 'DONE'
const NEW_WINDOW_TITLE = 'RUN'


function log_ex(message, loc) {
	// location parametr is not yet working as expected link to source line, but better than nothing

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


function unsafeQuerySelector(selector)
	{
	let elem = document.querySelector(selector)
	if (!elem)
		throw new Error(`Selector {selector} not found, possibly outdated`);
	return elem;
	}


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


async function waitUntil(untilFunc, maxTimeoutSec=10, intervalsSec=0.2) {
	let maxIt = Math.round(maxTimeoutSec * 1000 / intervalsSec);
	for (let i = 0; i < maxIt; i++)
		{
		await sleep(intervalsSec * 1000)
        if (untilFunc())
            return;
		if (i % 50 == 0)
			log_ex(`Waiting for winapi command fired extrernally ${i * intervalsSec}s`, location);
		}
}


function inFocusedTree(elem, maxDepth=5) {
	if (!document.activeElement)
		return False;
	let contains = document.activeElement.contains(elem);
	let depth = $(elem).parents().length - $(document.activeElement).parents().length;
	return contains && depth < maxDepth;
}


function requestTrustedClick(elem)
	{
	let xy = getClientPosPx(elem, true)
	document.title = REQ_CLICK.replace('${X}', xy.x).replace('${Y}', xy.y);
	}


function requestTrustedKeys(elem, keys)
	{
	elem.focus()
	document.title = REQ_KEYS.replace('${K}', keys);
	}


async function trustedSelect(selector)
	{
	let xy = getClientPosPx(elem, true)
	document.title = REQ_CLICK.replace('${X}', xy.x).replace('${Y}', xy.y);
	}


async function main()
	{
	// Not required since google auto focuses on the search,
	// but focus switch just to ensure clciks are working correctly
	let logo = unsafeQuerySelector(CSS_SEL_GOOGLE_LOGO);
	requestTrustedClick(logo);
	await waitUntil(() => inFocusedTree(logo));

	let search = unsafeQuerySelector(CSS_SEL_GOOGLE_SEARCH);
	requestTrustedClick(search);
	await waitUntil(() => inFocusedTree(search));

    await requestTrustedKeys(search, 'H e l l o Space W o r l d');
	await waitUntil(() => search.textLength == 'Hello World'.length);

    await requestTrustedKeys(search, 'Enter');
	let prevTitle = document.title;
    await waitUntil(() => document.title != prevTitle);

	log_ex('Demo script probably worked as expected', location)
	}


function open_new_tab(){
	// Unused. May be handy for background automation, since external clicks are possible to unfocused window
	log_ex('open_new_tab', location)
	let w = window.outerWidth;
	let h = window.outerWidth;
	let windowFeatures = `width=${w},height=${h},left=0,top=0`

	let currentURL = window.location.href
	let wnd = window.open(currentURL, "_blank", windowFeatures);
	if (!wnd) {
		log_ex('Cannot reference a new window, possibly popup was blocked.', location)
		return;
	}
}

main()
