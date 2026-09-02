// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'tipo_reserva.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$TipoReserva {

 int get id; int get laboratorioId; String get nombre; String get estado; String get createdAt; String get updatedAt; int? get createdBy; int? get updatedBy;
/// Create a copy of TipoReserva
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TipoReservaCopyWith<TipoReserva> get copyWith => _$TipoReservaCopyWithImpl<TipoReserva>(this as TipoReserva, _$identity);

  /// Serializes this TipoReserva to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is TipoReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.laboratorioId, laboratorioId) || other.laboratorioId == laboratorioId)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.createdBy, createdBy) || other.createdBy == createdBy)&&(identical(other.updatedBy, updatedBy) || other.updatedBy == updatedBy));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,laboratorioId,nombre,estado,createdAt,updatedAt,createdBy,updatedBy);

@override
String toString() {
  return 'TipoReserva(id: $id, laboratorioId: $laboratorioId, nombre: $nombre, estado: $estado, createdAt: $createdAt, updatedAt: $updatedAt, createdBy: $createdBy, updatedBy: $updatedBy)';
}


}

/// @nodoc
abstract mixin class $TipoReservaCopyWith<$Res>  {
  factory $TipoReservaCopyWith(TipoReserva value, $Res Function(TipoReserva) _then) = _$TipoReservaCopyWithImpl;
@useResult
$Res call({
 int id, int laboratorioId, String nombre, String estado, String createdAt, String updatedAt, int? createdBy, int? updatedBy
});




}
/// @nodoc
class _$TipoReservaCopyWithImpl<$Res>
    implements $TipoReservaCopyWith<$Res> {
  _$TipoReservaCopyWithImpl(this._self, this._then);

  final TipoReserva _self;
  final $Res Function(TipoReserva) _then;

/// Create a copy of TipoReserva
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? laboratorioId = null,Object? nombre = null,Object? estado = null,Object? createdAt = null,Object? updatedAt = null,Object? createdBy = freezed,Object? updatedBy = freezed,}) {
  return _then(TipoReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,laboratorioId: null == laboratorioId ? _self.laboratorioId : laboratorioId // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String,createdBy: freezed == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as int?,updatedBy: freezed == updatedBy ? _self.updatedBy : updatedBy // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

}


/// Adds pattern-matching-related methods to [TipoReserva].
extension TipoReservaPatterns on TipoReserva {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TipoReserva value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TipoReserva() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TipoReserva value)  $default,){
final _that = this;
switch (_that) {
case _TipoReserva():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TipoReserva value)?  $default,){
final _that = this;
switch (_that) {
case _TipoReserva() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  int laboratorioId,  String nombre,  String estado,  String createdAt,  String updatedAt,  int? createdBy,  int? updatedBy)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TipoReserva() when $default != null:
return $default(_that.id,_that.laboratorioId,_that.nombre,_that.estado,_that.createdAt,_that.updatedAt,_that.createdBy,_that.updatedBy);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  int laboratorioId,  String nombre,  String estado,  String createdAt,  String updatedAt,  int? createdBy,  int? updatedBy)  $default,) {final _that = this;
switch (_that) {
case _TipoReserva():
return $default(_that.id,_that.laboratorioId,_that.nombre,_that.estado,_that.createdAt,_that.updatedAt,_that.createdBy,_that.updatedBy);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  int laboratorioId,  String nombre,  String estado,  String createdAt,  String updatedAt,  int? createdBy,  int? updatedBy)?  $default,) {final _that = this;
switch (_that) {
case _TipoReserva() when $default != null:
return $default(_that.id,_that.laboratorioId,_that.nombre,_that.estado,_that.createdAt,_that.updatedAt,_that.createdBy,_that.updatedBy);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _TipoReserva implements TipoReserva {
  const _TipoReserva({required this.id, required this.laboratorioId, required this.nombre, required this.estado, required this.createdAt, required this.updatedAt, this.createdBy, this.updatedBy});
  factory _TipoReserva.fromJson(Map<String, dynamic> json) => _$TipoReservaFromJson(json);

@override final  int id;
@override final  int laboratorioId;
@override final  String nombre;
@override final  String estado;
@override final  String createdAt;
@override final  String updatedAt;
@override final  int? createdBy;
@override final  int? updatedBy;

/// Create a copy of TipoReserva
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TipoReservaCopyWith<_TipoReserva> get copyWith => __$TipoReservaCopyWithImpl<_TipoReserva>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TipoReservaToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _TipoReserva&&(identical(other.id, id) || other.id == id)&&(identical(other.laboratorioId, laboratorioId) || other.laboratorioId == laboratorioId)&&(identical(other.nombre, nombre) || other.nombre == nombre)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt)&&(identical(other.createdBy, createdBy) || other.createdBy == createdBy)&&(identical(other.updatedBy, updatedBy) || other.updatedBy == updatedBy));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,laboratorioId,nombre,estado,createdAt,updatedAt,createdBy,updatedBy);

@override
String toString() {
  return 'TipoReserva(id: $id, laboratorioId: $laboratorioId, nombre: $nombre, estado: $estado, createdAt: $createdAt, updatedAt: $updatedAt, createdBy: $createdBy, updatedBy: $updatedBy)';
}


}

/// @nodoc
abstract mixin class _$TipoReservaCopyWith<$Res> implements $TipoReservaCopyWith<$Res> {
  factory _$TipoReservaCopyWith(_TipoReserva value, $Res Function(_TipoReserva) _then) = __$TipoReservaCopyWithImpl;
@override @useResult
$Res call({
 int id, int laboratorioId, String nombre, String estado, String createdAt, String updatedAt, int? createdBy, int? updatedBy
});




}
/// @nodoc
class __$TipoReservaCopyWithImpl<$Res>
    implements _$TipoReservaCopyWith<$Res> {
  __$TipoReservaCopyWithImpl(this._self, this._then);

  final _TipoReserva _self;
  final $Res Function(_TipoReserva) _then;

/// Create a copy of TipoReserva
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? laboratorioId = null,Object? nombre = null,Object? estado = null,Object? createdAt = null,Object? updatedAt = null,Object? createdBy = freezed,Object? updatedBy = freezed,}) {
  return _then(_TipoReserva(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,laboratorioId: null == laboratorioId ? _self.laboratorioId : laboratorioId // ignore: cast_nullable_to_non_nullable
as int,nombre: null == nombre ? _self.nombre : nombre // ignore: cast_nullable_to_non_nullable
as String,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as String,createdBy: freezed == createdBy ? _self.createdBy : createdBy // ignore: cast_nullable_to_non_nullable
as int?,updatedBy: freezed == updatedBy ? _self.updatedBy : updatedBy // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}

// dart format on
