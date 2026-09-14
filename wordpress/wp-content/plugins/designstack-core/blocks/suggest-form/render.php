<?php
/**
 * Разметка блока «Форма „Предложить ресурс"».
 *
 * Состояния: по умолчанию · ошибки полей · сбой отправки · лимит · ресурс уже есть.
 * Состояние «отправка» рисует браузер (этап 14): кнопка получает aria-busy.
 * Успех живёт на отдельной странице /suggest/thanks/ (карта URL этапа 07).
 *
 * @package designstack-core
 *
 * @var array    $attributes Атрибуты блока.
 * @var string   $content    Содержимое.
 * @var WP_Block $block      Блок.
 */

defined( 'ABSPATH' ) || exit;

$ds_state = designstack_core_suggest_state();

// В редакторе состояние выбирается в панели блока.
if ( is_admin() && ! empty( $attributes['preview'] ) ) {
	$ds_state['state'] = (string) $attributes['preview'];

	if ( 'error' === $ds_state['state'] ) {
		$ds_state['errors'] = array(
			'resource_url'     => __( 'Это не похоже на адрес сайта. Проверь, нет ли пробела или опечатки, например: https://excalidraw.com', 'designstack-core' ),
			'resource_consent' => __( 'Без согласия с политикой данных предложение не отправить', 'designstack-core' ),
		);
	}
}

$ds_errors = $ds_state['errors'];
$ds_input  = $ds_state['input'];
$ds_value  = static fn( string $key ) => isset( $ds_input[ $key ] ) ? (string) $ds_input[ $key ] : '';

$ds_out = '';

// Сводка ошибок: первой, с фокусом на ней (этап 14).
if ( $ds_errors ) {
	$ds_items = '';

	foreach ( $ds_errors as $ds_field => $ds_message ) {
		$ds_items .= sprintf(
			'<li><a class="ds-link" href="#ds-suggest-%1$s">%2$s</a></li>',
			esc_attr( str_replace( 'resource_', '', $ds_field ) ),
			esc_html( $ds_message )
		);
	}

	$ds_out .= sprintf(
		'<div class="ds-error-summary" tabindex="-1"><p class="ds-error-summary__title">%1$s%2$s</p><ul class="ds-error-summary__list">%3$s</ul></div>',
		designstack_core_icon( 'circle-x' ),
		esc_html__( 'Проверь форму', 'designstack-core' ),
		$ds_items
	);
}

if ( 'failed' === $ds_state['state'] ) {
	$ds_out .= designstack_core_render_notice(
		'info',
		'info',
		'',
		__( 'Не получилось отправить: сервер не ответил. Введённое осталось в форме — отправь ещё раз через минуту.', 'designstack-core' )
	);
}

if ( 'limit' === $ds_state['state'] ) {
	$ds_out .= designstack_core_render_notice(
		'info',
		'info',
		'',
		__( 'С этого подключения за час уже пришло три предложения. Попробуй ещё раз через час — так мы защищаемся от спама.', 'designstack-core' )
	);
}

if ( 'duplicate' === $ds_state['state'] && $ds_state['known'] ) {
	$ds_known = (int) $ds_state['known'];
	$ds_out  .= sprintf(
		'<div class="ds-notice ds-notice--info">%1$s<div class="ds-notice__body"><p class="ds-notice__text"><a class="ds-link" href="%2$s">%3$s</a> %4$s</p></div></div>',
		designstack_core_icon( 'info' ),
		esc_url( get_permalink( $ds_known ) ),
		esc_html( get_the_title( $ds_known ) ),
		esc_html__( 'уже есть в каталоге', 'designstack-core' )
	);
}

$ds_consent_error = $ds_errors['resource_consent'] ?? '';
$ds_privacy       = get_page_by_path( 'privacy' );
$ds_privacy_url   = $ds_privacy ? get_permalink( $ds_privacy ) : home_url( '/privacy/' );

$ds_fields = designstack_core_suggest_field(
	'resource_url',
	__( 'Адрес ресурса', 'designstack-core' ),
	'url',
	$ds_value( 'resource_url' ),
	$ds_errors,
	true,
	'',
	'https://'
);

$ds_fields .= designstack_core_suggest_field(
	'resource_name',
	__( 'Название', 'designstack-core' ),
	'text',
	$ds_value( 'resource_name' ),
	$ds_errors
);

$ds_fields .= designstack_core_suggest_field(
	'resource_comment',
	__( 'Комментарий', 'designstack-core' ),
	'textarea',
	$ds_value( 'resource_comment' ),
	$ds_errors,
	false,
	__( 'Чем ресурс полезен и кому подойдёт', 'designstack-core' )
);

$ds_fields .= designstack_core_suggest_field(
	'resource_email',
	__( 'Почта', 'designstack-core' ),
	'email',
	$ds_value( 'resource_email' ),
	$ds_errors,
	false,
	__( 'Напишем, взяли ресурс в каталог или нет', 'designstack-core' )
);

$ds_fields .= sprintf(
	'<div class="ds-field ds-field--checkbox%1$s"><input type="checkbox" id="ds-suggest-consent" name="resource_consent" value="1" required%2$s%3$s>'
	. '<label class="ds-field__label" for="ds-suggest-consent">%4$s <a class="ds-link" href="%5$s">%6$s</a></label>%7$s</div>',
	$ds_consent_error ? ' is-error' : '',
	checked( ! empty( $ds_input['resource_consent'] ), true, false ),
	$ds_consent_error ? ' aria-invalid="true" aria-describedby="ds-suggest-consent-error"' : '',
	esc_html__( 'Соглашаюсь с', 'designstack-core' ),
	esc_url( $ds_privacy_url ),
	esc_html__( 'политикой данных', 'designstack-core' ),
	$ds_consent_error ? '<p class="ds-field__error" id="ds-suggest-consent-error">' . designstack_core_icon( 'circle-x' ) . esc_html( $ds_consent_error ) . '</p>' : ''
);

$ds_wrapper = get_block_wrapper_attributes( array( 'class' => 'ds-suggest-form' ) );

// phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- разметка собрана с экранированием, kses вырезал бы svg иконок.
printf(
	'%1$s<form %2$s id="ds-suggest-form" method="post" action="%3$s" novalidate>%4$s%5$s'
	. '<div class="ds-suggest-form__trap" aria-hidden="true"><label>%6$s<input type="text" name="resource_site" tabindex="-1" autocomplete="off"></label></div>'
	. '<button type="submit" class="ds-button ds-button--primary ds-button--lg ds-suggest-form__submit" data-ds-sending="Отправляем…">%7$s</button></form>',
	$ds_out,
	$ds_wrapper,
	esc_url( admin_url( 'admin-post.php' ) ),
	wp_nonce_field( 'designstack_suggest', 'designstack_suggest_nonce', true, false )
	. '<input type="hidden" name="action" value="designstack_suggest">',
	$ds_fields,
	esc_html__( 'Не заполняй это поле', 'designstack-core' ),
	esc_html__( 'Предложить ресурс', 'designstack-core' )
);
