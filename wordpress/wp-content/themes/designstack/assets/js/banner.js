/**
 * Баннер карты компетенций знает, проходил ли человек проверку.
 *
 * Сервер этого знать не может: ответы лежат в браузере, аккаунтов нет (D18).
 * Поэтому разметка приходит в состоянии «проверку ещё не проходили», а скрипт
 * переключает её, прочитав тот же ключ, что и сама проверка с картой.
 *
 * Три состояния, и разница между ними важная:
 * — ответов нет: приглашение пройти проверку;
 * — ответы есть, но не все: «Продолжить проверку», потому что бросать на середине
 *   и начинать сначала — худшее, что можно предложить;
 * — отвечено на все: человеку нужна карта развития, а не тест заново. Ссылка
 *   «пройти заново» остаётся рядом мелкой строкой.
 */
( function () {
	'use strict';

	var root = document.querySelector( '[data-banner]' );

	if ( ! root ) {
		return;
	}

	var map = root.getAttribute( 'data-banner-map' );
	var total = parseInt( root.getAttribute( 'data-banner-total' ), 10 ) || 0;
	var action = root.querySelector( '[data-banner-action]' );
	var lead = root.querySelector( '[data-banner-lead]' );
	var again = root.querySelector( '[data-banner-again]' );

	if ( ! action || ! map || ! total ) {
		return;
	}

	// Адрес проверки берём до подмены: он же нужен ссылке «пройти заново».
	var check = action.getAttribute( 'href' );
	var answers = null;

	try {
		answers = JSON.parse( localStorage.getItem( 'designstack-grade-check' ) || 'null' );
	} catch ( e ) {
		answers = null;
	}

	if ( ! answers || 'object' !== typeof answers ) {
		return;
	}

	var done = 0;
	var slug;

	for ( slug in answers ) {
		if ( Object.prototype.hasOwnProperty.call( answers, slug ) && 'number' === typeof answers[ slug ] ) {
			done++;
		}
	}

	if ( ! done ) {
		return;
	}

	if ( done < total ) {
		action.textContent = 'Продолжить проверку';

		if ( lead ) {
			lead.textContent = 'Проверка начата: отвечено ' + done + ' из ' + total +
				'. Ответы сохранились, можно продолжить с того же места.';
		}

		return;
	}

	action.setAttribute( 'href', map );
	action.setAttribute( 'data-track', 'map-open' );
	action.textContent = 'Открыть карту развития';

	if ( lead ) {
		lead.textContent = 'Проверка пройдена. В карте видно, где вы сейчас по каждому навыку и какой урок открыт дальше.';
	}

	if ( again ) {
		var link = document.createElement( 'a' );

		link.className = 'ds-banner__again-link';
		link.href = check;
		link.textContent = 'Пройти проверку заново';

		again.appendChild( link );
		again.hidden = false;
	}
}() );
