<?php
/**
 * Разметка каталога: карточка, метки, пустое состояние, факты.
 *
 * Классы и порядок частей повторяют паттерны темы — раздел «Контракт разметки
 * для этапа 12» в docs/ds/components.md. Нового класса здесь не появляется:
 * сначала запись в каталоге паттернов, потом код.
 *
 * CSS живёт в теме (assets/css/patterns.css), здесь только разметка.
 *
 * @package designstack-core
 */

defined( 'ABSPATH' ) || exit;

/**
 * Иконка из спрайта темы.
 *
 * Данные не зависят от темы: если темы DesignStack нет, метка остаётся словом —
 * статус читается и без иконки.
 *
 * @param string $name Имя иконки.
 * @return string Разметка svg или пустая строка.
 */
function designstack_core_icon( string $name ): string {
	return function_exists( 'designstack_icon' ) ? designstack_icon( $name ) : '';
}

/**
 * Соединяет значения серединной точкой.
 *
 * Перед точкой стоит неразрывный пробел: иначе при переносе строки точка уезжает
 * в начало следующей и висит там одна («UI и визуал / · / Прототипирование»).
 *
 * @param array<int, string> $items Значения.
 * @return string
 */
function designstack_core_join( array $items ): string {
	$items = array_values( array_filter( array_map( 'strval', $items ), 'strlen' ) );

	return implode( "\u{00A0}\u{00B7} ", $items );
}

/**
 * Метка.
 *
 * @param string $text    Слово словаря.
 * @param string $variant success | warning | error | tint-warning | tint-error | ''.
 * @param string $icon    Имя иконки или ''.
 * @param string $extra   Дополнительный класс.
 * @return string
 */
function designstack_core_badge( string $text, string $variant = '', string $icon = '', string $extra = '' ): string {
	if ( '' === $text ) {
		return '';
	}

	$classes = 'ds-badge'
		. ( $variant ? ' ds-badge--' . $variant : '' )
		. ( $extra ? ' ' . $extra : '' );

	return sprintf(
		'<span class="%1$s">%2$s%3$s</span>',
		esc_attr( $classes ),
		$icon ? designstack_core_icon( $icon ) : '',
		esc_html( $text )
	);
}

/**
 * Вариант и иконка метки по значению поля доступа или оплаты.
 *
 * Пара «иконка + цвет» — таблица «Статусы каталога → семантика» в foundation.md.
 *
 * @param string $key   Ключ поля: ru_open или ru_payment.
 * @param string $value Значение.
 * @return array{0: string, 1: string} Вариант и иконка.
 */
function designstack_core_status_look( string $key, string $value ): array {
	$map = array(
		'ru_open'    => array(
			'open'     => array( 'success', 'circle-check' ),
			'unstable' => array( 'warning', 'triangle-alert' ),
			'blocked'  => array( 'error', 'circle-x' ),
		),
		'ru_payment' => array(
			'payable'      => array( 'success', 'circle-check' ),
			'intermediary' => array( 'warning', 'triangle-alert' ),
			'no_payment'   => array( 'error', 'circle-x' ),
			'ru_native'    => array( 'success', 'circle-check' ),
		),
	);

	return $map[ $key ][ $value ] ?? array( '', '' );
}

/**
 * Расшифровка метки доступа или оплаты — та же, что в docs/VOICE.md.
 *
 * @param string $key   Ключ поля.
 * @param string $value Значение.
 * @return string
 */
function designstack_core_status_hint( string $key, string $value ): string {
	$hints = array(
		'ru_open'    => array(
			'open'     => __( 'Сайт открывается из России напрямую.', 'designstack-core' ),
			'unstable' => __( 'Сайт из России отвечает, но скорость ограничивают: видео и тяжёлые страницы грузятся неровно.', 'designstack-core' ),
			'blocked'  => __( 'Заблокирован или сам закрыл доступ пользователям из России.', 'designstack-core' ),
		),
		'ru_payment' => array(
			'payable'      => __( 'Платный тариф можно оплатить российской картой или в рублях.', 'designstack-core' ),
			'intermediary' => __( 'Российской картой не оплатить: платят картой СНГ или через посредника.', 'designstack-core' ),
			'no_payment'   => __( 'Российской картой не оплатить: нужен зарубежный счёт.', 'designstack-core' ),
			'ru_native'    => __( 'Российский сервис: рубли, документы, поддержка на русском.', 'designstack-core' ),
		),
	);

	return $hints[ $key ][ $value ] ?? '';
}

/**
 * Метки ресурса: цена, доступ из РФ, оплата из РФ.
 *
 * У бесплатного ресурса метки оплаты нет (D28).
 *
 * @param int $post_id Идентификатор записи.
 * @return string
 */
function designstack_core_badges( int $post_id ): string {
	$pricing = designstack_core_get_field( $post_id, 'pricing' );
	$out     = designstack_core_badge( designstack_core_enum_label( 'pricing', $pricing ) );

	foreach ( array( 'ru_open', 'ru_payment' ) as $key ) {
		$value = designstack_core_get_field( $post_id, $key );

		if ( 'ru_payment' === $key && 'free' === $pricing ) {
			continue;
		}

		list( $variant, $icon ) = designstack_core_status_look( $key, $value );
		$out                   .= designstack_core_badge( designstack_core_enum_label( $key, $value ), $variant, $icon );
	}

	return $out ? '<div class="ds-badges">' . $out . '</div>' : '';
}

/**
 * Состояние записи: закрыт, условия изменились, давно не проверяли.
 *
 * @param int $post_id Идентификатор записи.
 * @return array{0: string, 1: string, 2: string} Слово, вариант, иконка. Пусто, если состояние обычное.
 */
function designstack_core_state( int $post_id ): array {
	$status = designstack_core_get_field( $post_id, 'status' );

	if ( 'dead' === $status ) {
		return array( designstack_core_enum_label( 'status', 'dead' ), 'tint-error', 'circle-x' );
	}

	if ( 'changed' === $status ) {
		return array( designstack_core_enum_label( 'status', 'changed' ), 'tint-warning', 'triangle-alert' );
	}

	if ( designstack_core_is_stale( $post_id ) ) {
		return array( __( 'Давно не проверяли', 'designstack-core' ), 'tint-warning', 'clock' );
	}

	return array( '', '', '' );
}

/**
 * Проверяли ли ресурс больше 90 дней назад (P8).
 *
 * @param int $post_id Идентификатор записи.
 * @return bool
 */
function designstack_core_is_stale( int $post_id ): bool {
	$checked = designstack_core_get_field( $post_id, 'checked_at' );

	if ( ! $checked ) {
		return false;
	}

	return strtotime( $checked ) < strtotime( '-90 days', current_time( 'timestamp' ) );
}

/**
 * Строка даты проверки словами словаря.
 *
 * @param int $post_id Идентификатор записи.
 * @return string
 */
function designstack_core_checked_line( int $post_id ): string {
	$checked = designstack_core_get_field( $post_id, 'checked_at' );

	if ( ! $checked ) {
		return '';
	}

	$time = strtotime( $checked );

	/* translators: %s — дата вида «3 сен 2026». */
	return sprintf(
		__( 'Проверено %s', 'designstack-core' ),
		date_i18n( 'j', $time ) . "\u{00A0}" . mb_strtolower( date_i18n( 'M', $time ) ) . ' ' . date_i18n( 'Y', $time )
	);
}

/**
 * Уровень заголовка для списка, вставленного в содержимое записи.
 *
 * Куратор ставит список где хочет: сразу под H1 записи или внутри своей секции с H2. Уровень
 * карточки считается от последнего заголовка, который страница уже напечатала, — иначе в одном
 * случае получается пропуск уровня, в другом повтор. Заголовки своих блоков плагин печатает
 * вместе с карточками и уровень им задаёт сам, поэтому сюда они не попадают.
 *
 * @return int Уровень от 2 до 4.
 */
function designstack_core_heading_level(): int {
	$last = (int) ( $GLOBALS['designstack_core_last_heading'] ?? 1 );

	return min( 4, max( 2, $last + 1 ) );
}

/**
 * Запоминает уровень последнего заголовка страницы.
 *
 * @param string $content Разметка блока.
 * @return string
 */
function designstack_core_track_heading( string $content ): string {
	if ( preg_match_all( '/<h([1-4])[\s>]/i', $content, $found ) ) {
		$GLOBALS['designstack_core_last_heading'] = (int) end( $found[1] );
	}

	return $content;
}
add_filter( 'render_block', 'designstack_core_track_heading' );

/**
 * Карточка ресурса — одна на все списки (US-26).
 *
 * Уровень заголовка задаёт место: в архиве карточка идёт сразу под H1 страницы,
 * внутри секции с собственным H2 — на ступень ниже. Иначе в структуре пропуск уровня.
 *
 * @param int $post_id Идентификатор записи.
 * @param int $level   Уровень заголовка карточки, 2..4.
 * @return string
 */
function designstack_core_render_card( int $post_id, int $level = 3 ): string {
	$post = get_post( $post_id );

	if ( ! $post || 'resource' !== $post->post_type ) {
		return '';
	}

	$type      = designstack_core_get_type( $post_id );
	$type_term = $type ? get_term_by( 'slug', $type, 'resource_type' ) : null;
	$title     = get_the_title( $post_id );
	$verdict   = designstack_core_get_field( $post_id, 'verdict' );
	$url       = designstack_core_get_field( $post_id, 'url' );
	$status    = designstack_core_get_field( $post_id, 'status' );
	$analogs   = designstack_core_get_field( $post_id, 'ru_alternative' );
	$topics    = get_the_terms( $post_id, 'topic' );
	$date      = designstack_core_checked_line( $post_id );
	$tag       = 'h' . min( 4, max( 2, $level ) );

	list( $state_text, $state_variant, $state_icon ) = designstack_core_state( $post_id );

	$out = sprintf( '<article class="ds-card%s">', $type ? ' ds-card--' . esc_attr( $type ) : '' );

	$out .= '<div class="ds-card__head">';
	$out .= sprintf(
		'<span class="ds-logo" aria-hidden="true">%s</span>',
		// Буква одна на все плитки: без верхнего регистра строчная «u» у unDraw ломает ряд.
		esc_html( mb_strtoupper( mb_substr( $title, 0, 1 ) ) )
	);
	// Обёртка заголовка — div: <span> внутри себя заголовок не допускает, разметка невалидна.
	$out .= '<div class="ds-card__titles">';
	$out .= sprintf(
		'<%1$s class="ds-card__title"><a class="ds-card__link" href="%2$s">%3$s</a></%1$s>',
		$tag,
		esc_url( get_permalink( $post_id ) ),
		esc_html( $title )
	);

	if ( $type_term ) {
		$out .= sprintf( '<span class="ds-card__type">%s</span>', esc_html( $type_term->name ) );
	}

	$out .= '</div></div>';

	if ( $state_text ) {
		$out .= designstack_core_badge( $state_text, $state_variant, $state_icon, 'ds-card__state' );
	}

	if ( $verdict ) {
		$out .= sprintf( '<p class="ds-card__verdict">%s</p>', esc_html( $verdict ) );
	}

	$out .= designstack_core_badges( $post_id );

	if ( $topics && ! is_wp_error( $topics ) ) {
		$names = wp_list_pluck( array_slice( $topics, 0, 3 ), 'name' );
		$out  .= sprintf( '<p class="ds-card__tags">%s</p>', esc_html( designstack_core_join( $names ) ) );
	}

	$out .= '<div class="ds-card__foot">';

	if ( $date ) {
		$out .= sprintf( '<p class="ds-meta ds-meta--xs ds-card__date">%s</p>', esc_html( $date ) );
	}

	// У закрытого ресурса кнопки «Перейти на сайт» нет: вместо неё аналог (D31).
	if ( 'dead' === $status ) {
		if ( $analogs ) {
			$out .= sprintf(
				'<span class="ds-card__action"><a class="ds-button ds-button--secondary ds-button--sm" href="%1$s#analogs">%2$s</a></span>',
				esc_url( get_permalink( $post_id ) ),
				esc_html__( 'Показать аналог', 'designstack-core' )
			);
		}
	} elseif ( $url ) {
		// Переход на сайт ресурса — главное действие каталога: по нему видно,
		// что человек нашёл искомое (цель resource_outbound, docs/analytics/goals.md).
		$out .= sprintf(
			'<span class="ds-card__action"><a class="ds-button ds-button--secondary ds-button--sm" href="%1$s" target="_blank" rel="noopener"'
			. ' data-track="resource_outbound" %4$s>%2$s<span class="screen-reader-text">%3$s</span></a></span>',
			esc_url( $url ),
			esc_html__( 'Перейти на сайт', 'designstack-core' ),
			esc_html__( 'откроется в новой вкладке', 'designstack-core' ),
			designstack_core_track_attrs( $post_id )
		);
	}

	$out .= '</div></article>';

	return $out;
}

/**
 * Пустое состояние списка.
 *
 * @param string $variant Вариант: filters | section | search.
 * @param string $title   Заголовок из словаря.
 * @param string $text    Пояснение или ''.
 * @param string $actions Разметка действий или ''.
 * @return string
 */
function designstack_core_render_empty( string $variant, string $title, string $text = '', string $actions = '', string $heading = 'h2' ): string {
	$illustration = '';

	if ( function_exists( 'designstack_illustration' ) ) {
		$art          = 'not-found' === $variant ? 'not-found' : ( 'section' === $variant ? 'empty-section' : 'empty-filters' );
		$illustration = designstack_illustration( $art );
	}

	// На странице 404 заголовок пустого состояния — единственный h1 страницы.
	$heading = 'h1' === $heading ? 'h1' : 'h2';

	return sprintf(
		'<section class="ds-empty ds-empty--%1$s">%2$s<%6$s class="ds-empty__title">%3$s</%6$s>%4$s%5$s</section>',
		esc_attr( $variant ),
		$illustration,
		esc_html( $title ),
		$text ? '<p class="ds-empty__text">' . esc_html( $text ) . '</p>' : '',
		$actions ? '<div class="ds-empty__actions">' . $actions . '</div>' : '',
		$heading
	);
}

/**
 * Уведомление на странице ресурса.
 *
 * @param string $variant dead | changed | stale | info.
 * @param string $icon    Имя иконки.
 * @param string $title   Заголовок или ''.
 * @param string $text    Текст.
 * @param string $action  Разметка кнопки или ''.
 * @return string
 */
function designstack_core_render_notice( string $variant, string $icon, string $title, string $text, string $action = '' ): string {
	return sprintf(
		'<div class="ds-notice ds-notice--%1$s">%2$s<div class="ds-notice__body">%3$s<p class="ds-notice__text">%4$s</p>%5$s</div></div>',
		esc_attr( $variant ),
		designstack_core_icon( $icon ),
		$title ? '<p class="ds-notice__title">' . esc_html( $title ) . '</p>' : '',
		esc_html( $text ),
		$action
	);
}

/**
 * Как показать значение поля человеку.
 *
 * @param int    $post_id Идентификатор записи.
 * @param string $key     Ключ поля.
 * @return string Готовая разметка значения или '' — поля нет.
 */
function designstack_core_field_value( int $post_id, string $key ): string {
	$fields = designstack_core_fields();

	if ( ! isset( $fields[ $key ] ) ) {
		return '';
	}

	$field = $fields[ $key ];
	$value = designstack_core_get_field( $post_id, $key );

	if ( 'boolean' === $field['type'] ) {
		return $value ? esc_html__( 'есть', 'designstack-core' ) : esc_html__( 'нет', 'designstack-core' );
	}

	if ( is_array( $value ) ) {
		if ( ! $value ) {
			return '';
		}

		if ( 'file_format' === $key ) {
			$known = designstack_core_file_formats();
			$words = array_map( static fn( $item ) => $known[ $item ] ?? mb_strtoupper( (string) $item ), $value );

			return esc_html( designstack_core_join( $words ) );
		}

		if ( isset( $field['enum'] ) ) {
			$words = array_map( static fn( $item ) => designstack_core_enum_label( $field['enum'], (string) $item ), $value );

			return esc_html( designstack_core_join( $words ) );
		}

		return esc_html( designstack_core_join( (array) $value ) );
	}

	if ( '' === $value || 0 === $value ) {
		return '';
	}

	if ( isset( $field['enum'] ) ) {
		$label = designstack_core_enum_label( $field['enum'], (string) $value );

		if ( in_array( $key, array( 'ru_open', 'ru_payment' ), true ) ) {
			list( $variant, $icon ) = designstack_core_status_look( $key, (string) $value );

			return designstack_core_badge( $label, $variant, $icon );
		}

		return esc_html( $label );
	}

	return esc_html( (string) $value );
}

/**
 * Собирает одно поле формы.
 *
 * @param string                $key      Имя поля.
 * @param string                $label    Подпись.
 * @param string                $type     Тип поля.
 * @param string                $value    Значение.
 * @param array<string, string> $errors   Ошибки полей.
 * @param bool                  $required Обязательное ли поле.
 * @param string                $hint     Подсказка.
 * @param string                $placeholder Заполнитель.
 * @return string
 */
function designstack_core_suggest_field( string $key, string $label, string $type, string $value, array $errors, bool $required = false, string $hint = '', string $placeholder = '' ): string {
	$id      = 'ds-suggest-' . str_replace( 'resource_', '', $key );
	$error   = $errors[ $key ] ?? '';
	$hint_id = $hint ? $id . '-hint' : '';
	$err_id  = $error ? $id . '-error' : '';
	$aria    = trim( $err_id . ' ' . $hint_id );

	$classes = 'ds-field'
		. ( 'textarea' === $type ? ' ds-field--textarea' : '' )
		. ( $error ? ' is-error' : '' );

	$attrs = sprintf( 'id="%1$s" name="%2$s"', esc_attr( $id ), esc_attr( $key ) )
		. ( $required ? ' required' : '' )
		. ( $placeholder ? ' placeholder="' . esc_attr( $placeholder ) . '"' : '' )
		. ( $error ? ' aria-invalid="true"' : '' )
		. ( $aria ? ' aria-describedby="' . esc_attr( $aria ) . '"' : '' );

	$control = 'textarea' === $type
		? sprintf( '<textarea class="ds-field__control" %1$s rows="5" maxlength="1000">%2$s</textarea>', $attrs, esc_textarea( $value ) )
		: sprintf( '<input class="ds-field__control" type="%1$s" %2$s value="%3$s">', esc_attr( $type ), $attrs, esc_attr( $value ) );

	return sprintf(
		'<div class="%1$s"><label class="ds-field__label" for="%2$s">%3$s%4$s</label>%5$s%6$s%7$s</div>',
		esc_attr( $classes ),
		esc_attr( $id ),
		esc_html( $label ),
		$required ? '' : '<span class="ds-field__optional">' . esc_html__( 'необязательно', 'designstack-core' ) . '</span>',
		$control,
		$hint ? '<p class="ds-field__hint" id="' . esc_attr( $hint_id ) . '">' . esc_html( $hint ) . '</p>' : '',
		$error ? '<p class="ds-field__error" id="' . esc_attr( $err_id ) . '">' . designstack_core_icon( 'circle-x' ) . esc_html( $error ) . '</p>' : ''
	);
}
