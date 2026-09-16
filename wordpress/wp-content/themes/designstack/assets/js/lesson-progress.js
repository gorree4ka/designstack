/**
 * Память урока: место в тексте, итог тренажёра и отметка «пройден».
 *
 * Урок читают двадцать пять минут, и за один заход его почти никто не читает. До этой
 * правки страница не помнила ничего: перезагрузил — начинай сверху.
 *
 * Помним только то, что помогает вернуться, и ничего сверх того. Раскрытые замечания
 * в разборе чужого сценария нарочно не сохраняются: упражнение в том, чтобы сначала
 * найти их самому, и открытые с порога замечания урок обессмысливают.
 *
 * Место в тексте не прокручивается само: страница могла быть открыта по ссылке на
 * раздел, и прыжок из-под пальца читателя — это потеря управления. Вместо этого
 * наверху появляется строка с кнопкой «Продолжить».
 *
 * Всё лежит в браузере, рядом с ответами проверки грейда: аккаунтов на сайте нет (D18).
 */
( function () {
	'use strict';

	var nav = document.querySelector( '[data-lesson]' );

	if ( ! nav ) {
		return;
	}

	var slug = nav.getAttribute( 'data-lesson' );
	var KEY = 'designstack-lessons';
	var sections = Array.prototype.slice.call( document.querySelectorAll( '.ds-lesson__section[id]' ) );

	function readAll() {
		try {
			var kept = JSON.parse( localStorage.getItem( KEY ) || 'null' );

			return kept && 'object' === typeof kept ? kept : {};
		} catch ( e ) {
			return {};
		}
	}

	function read() {
		var one = readAll()[ slug ];

		return one && 'object' === typeof one ? one : {};
	}

	function write( patch ) {
		var all = readAll();
		var one = all[ slug ] && 'object' === typeof all[ slug ] ? all[ slug ] : {};
		var key;

		for ( key in patch ) {
			if ( Object.prototype.hasOwnProperty.call( patch, key ) ) {
				one[ key ] = patch[ key ];
			}
		}

		all[ slug ] = one;

		try {
			localStorage.setItem( KEY, JSON.stringify( all ) );
		} catch ( e ) {
			// Приватное окно или запрет на хранение: урок читается и без памяти.
		}
	}

	/**
	 * Заголовок раздела без номера: номер живёт отдельным элементом и в строке возврата лишний.
	 */
	function titleOf( section ) {
		var heading = section.querySelector( 'h2' );

		if ( ! heading ) {
			return '';
		}

		var clone = heading.cloneNode( true );
		var num = clone.querySelector( '.ds-lesson__num' );

		if ( num ) {
			num.parentNode.removeChild( num );
		}

		return clone.textContent.trim();
	}

	/* ---------- строка возврата ---------- */

	var saved = read();

	if ( saved.at && ! window.location.hash ) {
		var target = document.getElementById( saved.at );
		var name = target ? titleOf( target ) : '';

		if ( target && name ) {
			var bar = document.createElement( 'div' );
			var text = document.createElement( 'p' );
			var go = document.createElement( 'button' );

			bar.className = 'ds-resume';
			text.className = 'ds-resume__text';
			text.textContent = 'В прошлый раз вы читали до раздела «' + name + '»';

			go.type = 'button';
			go.className = 'ds-button ds-button--secondary ds-button--sm';
			go.textContent = 'Продолжить';
			go.addEventListener( 'click', function () {
				target.scrollIntoView( { behavior: 'smooth', block: 'start' } );
				bar.hidden = true;
			} );

			bar.appendChild( text );
			bar.appendChild( go );

			if ( sections.length ) {
				sections[ 0 ].parentNode.insertBefore( bar, sections[ 0 ] );
			}
		}
	}

	/* ---------- где человек читает сейчас ---------- */

	if ( sections.length && window.IntersectionObserver ) {
		var pending = '';
		var timer = null;

		function flush() {
			timer = null;

			if ( pending && pending !== read().at ) {
				write( { at: pending, ts: Date.now() } );
			}
		}

		var watcher = new window.IntersectionObserver(
			function ( entries ) {
				entries.forEach( function ( entry ) {
					// Раздел считается текущим, когда его начало ушло под верх экрана.
					if ( entry.isIntersecting ) {
						pending = entry.target.id;
					}
				} );

				if ( pending && ! timer ) {
					timer = window.setTimeout( flush, 1500 );
				}
			},
			{ rootMargin: '0px 0px -85% 0px' }
		);

		sections.forEach( function ( section ) {
			watcher.observe( section );
		} );

		// Вкладку закрывают чаще, чем ждут полторы секунды.
		window.addEventListener( 'pagehide', flush );
	}

	/* ---------- итог тренажёра ---------- */

	var quiz = document.querySelector( '[data-quiz]' );

	if ( quiz ) {
		if ( saved.quiz && 'number' === typeof saved.quiz.right ) {
			var was = document.createElement( 'p' );

			was.className = 'ds-quiz__was';
			was.textContent = 'В прошлый раз: ' + saved.quiz.right + ' из ' + saved.quiz.of;
			quiz.insertBefore( was, quiz.firstChild );
		}

		document.addEventListener( 'designstack:quiz-done', function ( event ) {
			write( { quiz: { right: event.detail.right, of: event.detail.total }, ts: Date.now() } );
		} );
	}

	/* ---------- отметка «пройден» ---------- */

	var holder = nav.querySelector( '[data-lesson-done]' );

	if ( holder ) {
		var mark = document.createElement( 'button' );

		function apply( done ) {
			mark.setAttribute( 'aria-pressed', done ? 'true' : 'false' );
			mark.textContent = done ? 'Урок отмечен пройденным' : 'Отметить урок пройденным';
			mark.className = 'ds-button ds-button--' + ( done ? 'primary' : 'secondary' );
		}

		mark.type = 'button';
		mark.addEventListener( 'click', function () {
			var now = ! read().done;

			write( { done: now, ts: Date.now() } );
			apply( now );
		} );

		apply( true === saved.done );
		holder.hidden = false;
		holder.appendChild( mark );
	}
}() );
