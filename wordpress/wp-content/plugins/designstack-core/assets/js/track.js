/**
 * Цели Яндекс Метрики.
 *
 * Ничего не знает про разметку страниц: слушает клики и отправки на документе
 * и смотрит атрибут data-track. Добавить цель — значит поставить атрибут в
 * шаблоне, а не править этот файл. Список целей — docs/analytics/goals.md.
 */
( function () {
	'use strict';

	var cfg = window.designstackMetrika || {};
	var id = cfg.id || 0;

	/**
	 * Отправляет цель. Без счётчика пишет в консоль — так видно локально,
	 * что цель сработала и с какими параметрами.
	 */
	function reach( goal, params ) {
		if ( ! goal ) {
			return;
		}

		var payload = Object.assign( {}, cfg.params || {}, params || {} );

		if ( id && typeof window.ym === 'function' ) {
			window.ym( id, 'reachGoal', goal, payload );

			return;
		}

		if ( window.console && console.debug ) {
			console.debug( 'designstack goal:', goal, payload );
		}
	}

	/** Читает data-track-* у элемента и его родителей. */
	function paramsOf( el ) {
		var out = {};

		Object.keys( el.dataset ).forEach( function ( key ) {
			if ( 0 === key.indexOf( 'track' ) && 'track' !== key && 'trackOnLoad' !== key ) {
				out[ key.slice( 5 ).replace( /^[A-Z]/, function ( c ) {
					return c.toLowerCase();
				} ).replace( /[A-Z]/g, function ( c ) {
					return '_' + c.toLowerCase();
				} ) ] = el.dataset[ key ];
			}
		} );

		return out;
	}

	// Наружу: переключатель темы живёт в теме и знает своё значение сам.
	window.designstackTrack = reach;

	document.addEventListener( 'click', function ( event ) {
		var el = event.target.closest( '[data-track]' );

		if ( el ) {
			reach( el.dataset.track, paramsOf( el ) );
		}
	}, true );

	document.addEventListener( 'submit', function ( event ) {
		var form = event.target.closest( 'form[data-track]' );

		if ( form ) {
			reach( form.dataset.track, paramsOf( form ) );
		}
	}, true );

	// Пустая выдача поиска — это не клик, а состояние страницы: цель шлём при загрузке.
	var empty = document.querySelector( '[data-track-on-load]' );

	if ( empty ) {
		reach( empty.dataset.trackOnLoad, paramsOf( empty ) );
	}

	// Ссылка юзер-теста: /?ut_task=tool-by-task. Метку кладём в параметры визита,
	// чтобы сегмент собирался штатными отчётами, а не выгрузкой руками.
	var task = new URLSearchParams( window.location.search ).get( 'ut_task' );

	if ( task && id && typeof window.ym === 'function' ) {
		window.ym( id, 'params', { ut_task: task } );
	}
}() );
