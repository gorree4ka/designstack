<?php
/**
 * Разметка блока «Оценка куратора».
 *
 * @package designstack-core
 *
 * @var array    $attributes Атрибуты блока.
 * @var string   $content    Содержимое.
 * @var WP_Block $block      Блок.
 */

defined( 'ABSPATH' ) || exit;

$ds_post_id = absint( $block->context['postId'] ?? get_the_ID() );

if ( ! $ds_post_id || 'resource' !== get_post_type( $ds_post_id ) ) {
	return;
}

// phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- разметка собрана с экранированием, kses вырезал бы svg иконок.
echo designstack_core_render_review( $ds_post_id );
