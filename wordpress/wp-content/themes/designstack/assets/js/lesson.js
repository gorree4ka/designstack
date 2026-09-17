/**
 * Урок: тренажёр и копирование готовых кусков.
 *
 * Тренажёр. Без скрипта все вопросы видны списком вместе с разбором: страница остаётся
 * полезной и попадает в поиск. Скрипт прячет разборы и показывает вопросы по одному,
 * считая счёт. Середина прохождения не сохраняется — вернуться на пятый вопрос из десяти
 * хуже, чем пройти две минуты заново, — а вот итог уходит событием `designstack:quiz-done`,
 * и его запоминает `lesson-progress.js`.
 *
 * Копирование. Сценарий и готовые формулировки человек уносит к себе, поэтому у них есть
 * кнопка. Без скрипта кнопки нет вовсе — текст всё равно виден и выделяется мышью.
 */
( function () {
	'use strict';

	// Кнопки копирования рисует скрипт: без него кнопка была бы мёртвой.
	Array.prototype.forEach.call( document.querySelectorAll( '[data-copy]' ), function ( holder ) {
		var target = document.getElementById( holder.getAttribute( 'data-copy' ) );

		if ( ! target || ! navigator.clipboard ) {
			return;
		}

		var button = document.createElement( 'button' );

		button.type = 'button';
		button.className = 'ds-button ds-button--secondary ds-button--sm';
		button.textContent = 'Скопировать';

		// Закрытые details в innerText не попадают: копировалась бы только раскрытая карточка.
		// На время чтения раскрываем все; атрибут name снимаем, иначе браузер держит
		// открытой одну и сам закрывает остальные.
		function textOf() {
			var state = Array.prototype.map.call( target.querySelectorAll( 'details' ), function ( one ) {
				return { node: one, open: one.open, name: one.getAttribute( 'name' ) };
			} );

			state.forEach( function ( one ) {
				one.node.removeAttribute( 'name' );
				one.node.open = true;
			} );

			var text = target.innerText.replace( /\n{3,}/g, '\n\n' ).trim();

			state.forEach( function ( one ) {
				one.node.open = one.open;

				if ( one.name ) {
					one.node.setAttribute( 'name', one.name );
				}
			} );

			return text;
		}

		button.addEventListener( 'click', function () {
			navigator.clipboard.writeText( textOf() ).then(
				function () {
					button.textContent = 'Скопировано';

					window.setTimeout( function () {
						button.textContent = 'Скопировать';
					}, 1800 );
				},
				function () {
					button.textContent = 'Не вышло — выделите текст';
				}
			);
		} );

		holder.appendChild( button );
	} );
}() );

/**
 * Переключатель панелей: черновик сценария и он же после чистки.
 *
 * Без скрипта видны обе панели со своими подписями — сравнивать даже удобнее, просто длиннее.
 * Скрипт прячет одну и включает кнопки; подписи панелей при этом убираются, их роль берут кнопки.
 */
( function () {
	'use strict';

	Array.prototype.forEach.call( document.querySelectorAll( '[data-switch]' ), function ( root ) {
		var buttons = Array.prototype.slice.call( root.querySelectorAll( '[data-switch-btn]' ) );
		var panes = Array.prototype.slice.call( root.querySelectorAll( '[data-switch-pane]' ) );

		if ( buttons.length < 2 || panes.length < 2 ) {
			return;
		}

		function show( key ) {
			panes.forEach( function ( pane ) {
				pane.hidden = pane.getAttribute( 'data-switch-pane' ) !== key;
			} );

			buttons.forEach( function ( button ) {
				button.setAttribute(
					'aria-pressed',
					button.getAttribute( 'data-switch-btn' ) === key ? 'true' : 'false'
				);
			} );
		}

		buttons.forEach( function ( button ) {
			button.hidden = false;
			button.addEventListener( 'click', function () {
				show( button.getAttribute( 'data-switch-btn' ) );
			} );
		} );

		root.classList.add( 'is-live' );
		show( buttons[ 0 ].getAttribute( 'data-switch-btn' ) );
	} );
}() );

/**
 * Показать и спрятать замечания в разборе чужого сценария.
 *
 * В разметке замечания видны: без скрипта страница не должна терять половину содержимого.
 * Скрипт прячет их и рисует кнопку — чтобы читатель сначала нашёл проблемы сам, а потом
 * сверился. Кнопки в разметке нет вовсе: без скрипта она была бы мёртвой.
 */
( function () {
	'use strict';

	Array.prototype.forEach.call( document.querySelectorAll( '[data-reveal]' ), function ( root ) {
		var holder = root.querySelector( '[data-reveal-button]' );
		var items = Array.prototype.slice.call( root.querySelectorAll( '[data-reveal-item]' ) );

		if ( ! holder || ! items.length ) {
			return;
		}

		var open = false;
		var button = document.createElement( 'button' );

		function apply() {
			items.forEach( function ( item ) {
				item.hidden = ! open;
			} );

			button.setAttribute( 'aria-pressed', open ? 'true' : 'false' );
			button.textContent = open ? 'Скрыть замечания' : 'Показать замечания';
		}

		button.type = 'button';
		button.className = 'ds-button ds-button--secondary ds-button--sm';
		button.addEventListener( 'click', function () {
			open = ! open;
			apply();
		} );

		holder.appendChild( button );
		root.classList.add( 'ds-reveal' );
		apply();
	} );
}() );

( function () {
	'use strict';

	var boxes = document.querySelectorAll( '[data-quiz]' );

	if ( ! boxes.length ) {
		return;
	}

	Array.prototype.forEach.call( boxes, function ( root ) {
		var items = Array.prototype.slice.call( root.querySelectorAll( '[data-quiz-q]' ) );
		var actions = root.querySelector( '[data-quiz-actions]' );
		var next = root.querySelector( '[data-quiz-next]' );
		var idx = root.querySelector( '[data-quiz-idx]' );
		var score = root.querySelector( '[data-quiz-score]' );
		var fill = root.querySelector( '[data-quiz-fill]' );
		var total = items.length;

		if ( ! total || ! actions || ! next ) {
			return;
		}

		var at = 0;
		var right = 0;
		var answered = false;

		function feedbackOf( item ) {
			return item.querySelector( '[data-quiz-feedback]' );
		}

		function show() {
			answered = false;

			items.forEach( function ( item, i ) {
				item.hidden = i !== at;

				var fb = feedbackOf( item );

				if ( fb ) {
					fb.hidden = true;
				}
			} );

			Array.prototype.forEach.call( actions.children, function ( btn ) {
				btn.disabled = false;
				btn.className = 'ds-quiz__option';
			} );

			actions.hidden = false;
			next.hidden = true;

			if ( idx ) {
				idx.textContent = String( at + 1 );
			}

			if ( fill ) {
				fill.style.width = Math.round( ( at / total ) * 100 ) + '%';
			}
		}

		// Ответ — строковый ключ, а не «верно / неверно»: вариантов в тренажёрах
		// бывает от двух до пяти, и называются они по-разному в каждом уроке.
		function answer( said, btn ) {
			if ( answered ) {
				return;
			}

			answered = true;

			var item = items[ at ];
			var hit = said === item.getAttribute( 'data-answer' );

			if ( hit ) {
				right++;
			}

			if ( score ) {
				score.textContent = right + ' верно';
			}

			btn.className = 'ds-quiz__option ' + ( hit ? 'is-right' : 'is-wrong' );

			Array.prototype.forEach.call( actions.children, function ( other ) {
				other.disabled = true;
			} );

			var fb = feedbackOf( item );

			if ( fb ) {
				fb.hidden = false;
				fb.setAttribute( 'tabindex', '-1' );
				fb.focus();
			}

			if ( fill ) {
				fill.style.width = Math.round( ( ( at + 1 ) / total ) * 100 ) + '%';
			}

			next.hidden = false;
			next.textContent = at === total - 1 ? 'Показать итог' : 'Дальше';
		}

		function finish() {
			var item = items[ at ];

			item.hidden = false;
			actions.hidden = true;

			var q = item.querySelector( '.ds-quiz__question' );
			var fb = feedbackOf( item );

			if ( q ) {
				q.textContent = 'Итог: ' + right + ' из ' + total;
			}

			if ( fb ) {
				fb.hidden = false;
				fb.innerHTML = '';

				var head = document.createElement( 'b' );

				head.textContent = 'Что это значит';
				fb.appendChild( head );
				fb.appendChild(
					document.createTextNode(
						right >= total - 1
							? 'На интервью вы будете ловить такие вопросы у себя в голове до того, как произнесёте.'
							: right >= Math.ceil( total * 0.7 )
								? 'Пара формулировок проскочила. Перечитайте раздел про прошлое и желания и пройдите тренажёр ещё раз перед первым интервью.'
								: 'Стоит вернуться к разделу про пять видов плохих вопросов: это ровно то место, где теряется большинство первых интервью.'
					)
				);
			}

			next.textContent = 'Пройти заново';
			next.hidden = false;

			// Итог отдаём наружу: где его хранить, тренажёр знать не должен.
			document.dispatchEvent(
				new CustomEvent( 'designstack:quiz-done', { detail: { right: right, total: total } } )
			);
		}

		next.addEventListener( 'click', function () {
			if ( 'Пройти заново' === next.textContent ) {
				at = 0;
				right = 0;

				if ( score ) {
					score.textContent = '0 верно';
				}

				items.forEach( function ( item ) {
					var q = item.querySelector( '.ds-quiz__question' );

					if ( q && q.getAttribute( 'data-text' ) ) {
						q.textContent = q.getAttribute( 'data-text' );
					}

					var fb = feedbackOf( item );

					if ( fb && fb.getAttribute( 'data-html' ) ) {
						fb.innerHTML = fb.getAttribute( 'data-html' );
					}
				} );

				show();

				return;
			}

			if ( at === total - 1 ) {
				finish();

				return;
			}

			at++;
			show();
		} );

		Array.prototype.forEach.call( actions.children, function ( btn ) {
			btn.addEventListener( 'click', function () {
				answer( btn.getAttribute( 'data-quiz-answer' ), btn );
			} );
		} );

		// Запоминаем исходный вид, чтобы «пройти заново» возвращал вопрос, а не итог.
		items.forEach( function ( item ) {
			var q = item.querySelector( '.ds-quiz__question' );
			var fb = feedbackOf( item );

			if ( q ) {
				q.setAttribute( 'data-text', q.textContent );
			}

			if ( fb ) {
				fb.setAttribute( 'data-html', fb.innerHTML );
			}
		} );

		// «Вопрос 1 из 10» и счёт над списком без скрипта были бы неправдой: в разметке они
		// скрыты, показывает их пошаговый режим.
		var meta = root.querySelector( '[data-quiz-meta]' );

		if ( meta ) {
			meta.hidden = false;
		}

		root.classList.add( 'is-stepped' );
		show();
	} );
}() );
